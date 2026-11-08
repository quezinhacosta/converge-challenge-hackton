"""Script de Fine-Tuning do Mistral-7B-Instruct-v0.3 com QLoRA (PEFT + TRL).

Modelo: https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3
Salva exclusivamente a camada de ajustes (LoRA Adapters) em `lora_adapters/`.

Requisitos de Hardware:
- GPU NVIDIA (CUDA): recomendado 12GB+ de VRAM (ou Google Colab gratuito com GPU T4).
- Se executado em CPU: requer no minimo 16GB a 24GB de memoria RAM livre.
"""

import argparse
import os
import sys


def check_hardware() -> tuple[bool, str]:
    try:
        import torch
    except ImportError:
        print("[ERRO] PyTorch nao esta instalado. Instale com: pip install torch")
        sys.exit(1)

    has_cuda = torch.cuda.is_available()
    if has_cuda:
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"[Hardware] GPU NVIDIA Detectada: {gpu_name} ({vram_gb:.1f} GB de VRAM)")
        return True, "cuda"
    else:
        print(
            "[Hardware] Nenhuma GPU NVIDIA com suporte a CUDA detectada. Modo CPU selecionado."
        )
        # Verifica memoria RAM
        try:
            import psutil

            mem_avail_gb = psutil.virtual_memory().available / (1024**3)
            print(f"[Hardware] Memoria RAM disponivel: {mem_avail_gb:.1f} GB")
            if mem_avail_gb < 14.0:
                print("\n" + "!" * 70)
                print("[ALERTA CRITICO DE HARDWARE]")
                print(f"O modelo Mistral-7B possui 14.5 GB de pesos brutos.")
                print(f"Sua maquina possui apenas {mem_avail_gb:.1f} GB de RAM livre.")
                print(
                    "Carregar o Mistral-7B em CPU nesta maquina causara estouro de memoria (OOM)."
                )
                print("Para treinar o Mistral-7B em 30 minutos sem travar seu PC:")
                print(
                    "-> Utilize o Google Colab gratuito com GPU T4 (veja train_mistral_colab.ipynb)"
                )
                print("!" * 70 + "\n")
        except ImportError:
            pass
        return False, "cpu"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fine-Tuning do Mistral-7B-Instruct-v0.3"
    )
    parser.add_argument(
        "--base_model",
        type=str,
        default="mistralai/Mistral-7B-Instruct-v0.3",
        help="Identificador do modelo base no Hugging Face",
    )
    parser.add_argument(
        "--train_file",
        type=str,
        default="train_dataset.jsonl",
        help="Arquivo de treino JSONL",
    )
    parser.add_argument(
        "--val_file",
        type=str,
        default="val_dataset.jsonl",
        help="Arquivo de validacao JSONL",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="lora_adapters",
        help="Pasta de saida onde a camada de ajustes (LoRA) sera salva",
    )
    parser.add_argument("--epochs", type=int, default=2, help="Numero de epocas")
    parser.add_argument("--batch_size", type=int, default=1, help="Batch size")
    parser.add_argument(
        "--grad_accum", type=int, default=8, help="Passos de acumulacao de gradiente"
    )
    parser.add_argument("--lr", type=float, default=2e-4, help="Learning rate")
    parser.add_argument("--lora_r", type=int, default=16, help="Rank LoRA (r=16)")
    parser.add_argument("--lora_alpha", type=int, default=32, help="Alpha LoRA")
    parser.add_argument(
        "--max_seq_length", type=int, default=1024, help="Comprimento maximo de tokens"
    )
    return parser.parse_args()


def main() -> None:
    has_cuda, device = check_hardware()
    args = parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    train_path = os.path.join(base_dir, args.train_file)
    val_path = os.path.join(base_dir, args.val_file)
    output_dir = os.path.join(base_dir, args.output_dir)

    try:
        import torch
        from datasets import load_dataset
        from peft import LoraConfig, TaskType
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from trl import SFTConfig, SFTTrainer
    except ImportError as e:
        print(f"[ERRO] Faltam dependencias: {e}")
        print("Instale com: pip install torch transformers peft trl datasets")
        sys.exit(1)

    print("=" * 65)
    print("      vitAI - Fine-Tuning do Mistral-7B-Instruct-v0.3")
    print("=" * 65)
    print(f"Modelo Base: {args.base_model}")
    print(f"Dispositivo: {device.upper()}")
    print(f"Saida da Camada de Ajustes: {output_dir}")
    print("=" * 65 + "\n")

    # 1. Carrega Tokenizer do Mistral v0.3
    print("1/4. Carregando Tokenizer do Mistral-7B-Instruct-v0.3...")
    tokenizer = AutoTokenizer.from_pretrained(args.base_model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # 2. Carrega Modelo Base
    print("2/4. Carregando pesos do Mistral-7B-Instruct-v0.3...")
    compute_dtype = (
        torch.bfloat16
        if (has_cuda and torch.cuda.is_bf16_supported())
        else torch.float16
    )

    if has_cuda:
        from transformers import BitsAndBytesConfig

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=compute_dtype,
            bnb_4bit_use_double_quant=True,
        )
        model = AutoModelForCausalLM.from_pretrained(
            args.base_model,
            quantization_config=bnb_config,
            device_map="auto",
            torch_dtype=compute_dtype,
            trust_remote_code=True,
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            args.base_model,
            device_map="cpu",
            torch_dtype=compute_dtype,
            trust_remote_code=True,
        )

    # 3. Configura LoRA
    print("3/4. Configurando camada de adaptadores LoRA...")
    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        lora_dropout=0.05,
        bias="none",
        task_type=TaskType.CAUSAL_LM,
    )

    # 4. Datasets
    print("4/4. Carregando datasets...")
    dataset = load_dataset(
        "json",
        data_files={"train": train_path, "validation": val_path},
    )

    training_args = SFTConfig(
        output_dir=output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        lr_scheduler_type="cosine",
        warmup_steps=10,
        logging_steps=10,
        save_strategy="epoch",
        eval_strategy="epoch",
        report_to="none",
        save_total_limit=1,
        max_length=args.max_seq_length,
        dataset_text_field="messages",
        use_cpu=(not has_cuda),
        fp16=(has_cuda and compute_dtype == torch.float16),
        bf16=(has_cuda and compute_dtype == torch.bfloat16),
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"],
        peft_config=lora_config,
        processing_class=tokenizer,
        args=training_args,
    )

    print("\nIniciando treinamento da camada de ajustes (LoRA)...")
    trainer.train()

    print(f"\nSalvando camada de ajustes em: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)
    trainer.model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    print("\n" + "=" * 65)
    print("[CONCLUIDO COM SUCESSO]")
    print(f"Camada de ajustes salva em: {output_dir}")
    print(f" - {os.path.join(output_dir, 'adapter_config.json')}")
    print(f" - {os.path.join(output_dir, 'adapter_model.safetensors')}")
    print("=" * 65)


if __name__ == "__main__":
    main()
