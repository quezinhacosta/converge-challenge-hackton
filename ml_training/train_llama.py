"""Script de Fine-Tuning do Llama-3.1-8B-Instruct com QLoRA (PEFT + TRL).

Este script carrega o modelo base `meta-llama/Llama-3.1-8B-Instruct` em 4-bit (NF4),
aplica adaptadores LoRA (Low-Rank Adaptation) em todas as camadas de atencao e MLP,
treina sobre o dataset de governanca da NR-1 e salva exclusivamente a camada de
ajustes (LoRA Adapters) em `lora_adapters/`.

Requisitos de Hardware:
- GPU NVIDIA com suporte a CUDA (12GB a 24GB de VRAM: RTX 3060/3080/4080/4090, A10, T4, L4).
- Token de acesso com permissao aprovada para o Llama 3.1 no Hugging Face (HF_TOKEN).
"""

import argparse
import os
import sys


def check_environment() -> None:
    try:
        import torch
    except ImportError:
        print("[ERRO] PyTorch nao esta instalado.")
        print("Instale com: pip install torch")
        sys.exit(1)

    if not torch.cuda.is_available():
        print("[ALERTA] Nenhuma GPU NVIDIA com suporte a CUDA foi detectada.")
        print("O fine-tuning do Llama-3.1-8B requer GPU dedicada.")
        print("Se voce possui uma GPU NVIDIA, verifique os drivers e CUDA.")
    else:
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"[OK] GPU Detectada: {gpu_name} ({vram_gb:.1f} GB de VRAM)")

    token = os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")
    if not token:
        # Verifica se já está logado via huggingface-cli
        hf_token_path = os.path.expanduser("~/.cache/huggingface/token")
        if not os.path.exists(hf_token_path):
            print("\n[IMPORTANTE] Token do Hugging Face nao detectado!")
            print("O modelo meta-llama/Llama-3.1-8B-Instruct e restrito pela Meta.")
            print("1. Aceite a licenca em: https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct")
            print("2. Gere um token em: https://huggingface.co/settings/tokens")
            print("3. Execute no terminal: export HF_TOKEN='seu_token_aqui'")
            print("   Ou execute: huggingface-cli login\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fine-Tuning do Llama-3.1-8B-Instruct com QLoRA")
    parser.add_argument(
        "--base_model",
        type=str,
        default="meta-llama/Llama-3.1-8B-Instruct",
        help="Identificador do modelo base no Hugging Face",
    )
    parser.add_argument(
        "--train_file",
        type=str,
        default="train_dataset.jsonl",
        help="Caminho do arquivo de treino em formato JSONL",
    )
    parser.add_argument(
        "--val_file",
        type=str,
        default="val_dataset.jsonl",
        help="Caminho do arquivo de validacao em formato JSONL",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="lora_adapters",
        help="Pasta de saida onde a camada de ajustes (LoRA) sera salva",
    )
    parser.add_argument("--epochs", type=int, default=3, help="Numero de epocas de treinamento")
    parser.add_argument("--batch_size", type=int, default=2, help="Batch size por dispositivo")
    parser.add_argument(
        "--grad_accum", type=int, default=4, help="Passos de acumulacao de gradiente"
    )
    parser.add_argument("--lr", type=float, default=2e-4, help="Learning rate (taxa de aprendizado)")
    parser.add_argument(
        "--lora_r", type=int, default=16, help="Rank da decomposicao LoRA (r=8, 16 ou 32)"
    )
    parser.add_argument("--lora_alpha", type=int, default=32, help="Escalar alpha do LoRA")
    parser.add_argument("--max_seq_length", type=int, default=1536, help="Comprimento maximo de tokens")
    return parser.parse_args()


def main() -> None:
    check_environment()
    args = parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    train_path = os.path.join(base_dir, args.train_file)
    val_path = os.path.join(base_dir, args.val_file)
    output_dir = os.path.join(base_dir, args.output_dir)

    if not os.path.exists(train_path):
        print(f"Dataset de treino nao encontrado em {train_path}.")
        print("Gerando dataset de instrucao primeiro...")
        from generate_llama_dataset import generate_full_dataset, save_jsonl

        data = generate_full_dataset(1200)
        split = int(len(data) * 0.85)
        save_jsonl(data[:split], train_path)
        save_jsonl(data[split:], val_path)
        print("Dataset gerado com sucesso!")

    # Importa bibliotecas de fine-tuning
    try:
        import torch
        from datasets import load_dataset
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            BitsAndBytesConfig,
            TrainingArguments,
        )
        from trl import SFTTrainer
    except ImportError as e:
        print(f"\n[ERRO] Faltam dependencias para o treinamento: {e}")
        print("Instale os requisitos com o comando:")
        print("pip install -r requirements.txt")
        sys.exit(1)

    print(f"\n=== Iniciando Pipeline de Fine-Tuning ===")
    print(f"Modelo Base: {args.base_model}")
    print(f"Camada de Ajustes de Saida: {output_dir}")
    print(f"Epocas: {args.epochs} | Batch Size Efetivo: {args.batch_size * args.grad_accum}")
    print(f"LoRA Rank (r): {args.lora_r} | Alpha: {args.lora_alpha}\n")

    # 1. Configuracao de Quantizacao 4-bit (QLoRA)
    compute_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=compute_dtype,
        bnb_4bit_use_double_quant=True,
    )

    # 2. Carrega o Tokenizer do Llama 3.1
    print("Carregando Tokenizer do Llama 3.1...")
    tokenizer = AutoTokenizer.from_pretrained(args.base_model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # 3. Carrega o Modelo Base quantizado
    print("Carregando pesos do modelo base em 4-bit NF4...")
    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=compute_dtype,
        trust_remote_code=True,
    )

    # 4. Prepara o modelo para treino k-bit e aplica LoRA
    model = prepare_model_for_kbit_training(model)

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
        task_type="CAUSAL_LM",
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # 5. Carrega o Dataset no formato chat
    print("\nCarregando datasets...")
    dataset = load_dataset(
        "json",
        data_files={"train": train_path, "validation": val_path},
    )

    # 6. Argumentos de Treinamento
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        logging_steps=10,
        save_strategy="epoch",
        evaluation_strategy="epoch",
        fp16=(compute_dtype == torch.float16),
        bf16=(compute_dtype == torch.bfloat16),
        optim="paged_adamw_8bit",
        report_to="none",
        save_total_limit=2,
    )

    # 7. SFT Trainer com Chat Template nativo do Llama 3.1
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"],
        peft_config=lora_config,
        dataset_text_field="messages",
        max_seq_length=args.max_seq_length,
        tokenizer=tokenizer,
        args=training_args,
    )

    print("\nIniciando treinamento da camada de ajustes (LoRA Adapters)...")
    trainer.train()

    # 8. Salvar exclusivamente a camada de ajustes (LoRA Adapters)
    print(f"\nSalvando camada de ajustes (LoRA) em: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)
    trainer.model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    print("\n[CONCLUIDO COM SUCESSO]")
    print(f"Camada de ajustes salva em: {output_dir}")
    print("Arquivos gerados:")
    print(f" - {os.path.join(output_dir, 'adapter_config.json')}")
    print(f" - {os.path.join(output_dir, 'adapter_model.safetensors')}")
    print("\nPara testar a inferencia do modelo adaptado, execute:")
    print("python3 run_inference.py")


if __name__ == "__main__":
    main()
