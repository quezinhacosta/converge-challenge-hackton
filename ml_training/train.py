"""Script de Treinamento e Fine-Tuning Otimizado para CPU e GPU.

Projetado para treinar com eficiencia em maquinas locais (com ou sem GPU NVIDIA dedicada).
Utiliza um modelo compacto de alta capacidade (SLM: Qwen2.5-0.5B-Instruct ou Qwen2.5-1.5B-Instruct)
que baixa menos de 1GB de dados, consome menos de 2.5GB de memoria RAM e treina em 20 a 40 minutos.

Salva exclusivamente a camada de ajustes (LoRA Adapters) em `lora_adapters/`.
"""

import argparse
import os
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Treinamento Eficiente vitAI NR-1 com LoRA")
    parser.add_argument(
        "--base_model",
        type=str,
        default="Qwen/Qwen2.5-0.5B-Instruct",
        help="Modelo base compacto (padrao: Qwen/Qwen2.5-0.5B-Instruct, ~900MB)",
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
        help="Pasta onde a camada de ajustes (LoRA) sera salva",
    )
    parser.add_argument("--epochs", type=int, default=2, help="Numero de epocas de treinamento")
    parser.add_argument("--batch_size", type=int, default=2, help="Batch size de treino")
    parser.add_argument(
        "--grad_accum", type=int, default=4, help="Passos de acumulacao de gradiente"
    )
    parser.add_argument("--lr", type=float, default=3e-4, help="Learning rate (taxa de aprendizado)")
    parser.add_argument("--lora_r", type=int, default=8, help="Rank da decomposicao LoRA (r=8)")
    parser.add_argument("--lora_alpha", type=int, default=16, help="Escalar alpha do LoRA")
    parser.add_argument("--max_seq_length", type=int, default=512, help="Comprimento maximo de tokens")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    train_path = os.path.join(base_dir, args.train_file)
    val_path = os.path.join(base_dir, args.val_file)
    output_dir = os.path.join(base_dir, args.output_dir)

    try:
        import torch
        from datasets import load_dataset
        from peft import LoraConfig, get_peft_model, TaskType
        from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
        from trl import SFTTrainer
    except ImportError as e:
        print(f"[ERRO] Faltam dependencias: {e}")
        print("Instale no seu ambiente com: pip install torch transformers peft trl datasets accelerate")
        sys.exit(1)

    has_cuda = torch.cuda.is_available()
    device = "cuda" if has_cuda else "cpu"

    print("=" * 65)
    print("      vitAI - Pipeline de Treinamento Otimizado (NR-1)")
    print("=" * 65)
    if has_cuda:
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"[Hardware] GPU NVIDIA Detectada: {gpu_name} ({vram_gb:.1f} GB VRAM)")
    else:
        cpu_count = os.cpu_count() or 4
        torch.set_num_threads(cpu_count)
        print(f"[Hardware] Modo CPU Ativo: {cpu_count} nucleos de processamento.")
        print("[Otimizacao] Modelo compacto selecionado: treino leve sem travar a maquina.")

    print(f"[Modelo Base] {args.base_model}")
    print(f"[Saida] Camada de Ajustes em: {output_dir}")
    print(f"[Configuracao] Epocas: {args.epochs} | LoRA Rank: {args.lora_r} | Max Tokens: {args.max_seq_length}")
    print("=" * 65 + "\n")

    # Verifica se os arquivos de dados existem
    if not os.path.exists(train_path):
        print(f"Dataset de treino nao encontrado em {train_path}. Gerando...")
        from generate_mistral_dataset import generate_full_dataset, save_jsonl

        data = generate_full_dataset(600)
        split = int(len(data) * 0.85)
        save_jsonl(data[:split], train_path)
        save_jsonl(data[split:], val_path)
        print("Dataset gerado com sucesso!")

    # 1. Carrega Tokenizer
    print("1/5. Carregando Tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(args.base_model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # 2. Carrega Modelo Base
    print("2/5. Carregando pesos do modelo base (download leve de ~900MB)...")
    torch_dtype = torch.float16 if has_cuda else torch.float32

    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        device_map=device,
        torch_dtype=torch_dtype,
        trust_remote_code=True,
    )

    # 3. Configura Adaptadores LoRA
    print("3/5. Injetando adaptadores LoRA para ajuste fino eficiente...")
    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type=TaskType.CAUSAL_LM,
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # 4. Carrega Datasets
    print("\n4/5. Preparando datasets de treino e validacao...")
    dataset = load_dataset(
        "json",
        data_files={"train": train_path, "validation": val_path},
    )

    # Limita amostras para garantir treino rapido no CPU (< 1h)
    train_dataset = dataset["train"]
    val_dataset = dataset["validation"]
    if not has_cuda and len(train_dataset) > 400:
        train_dataset = train_dataset.select(range(400))
        val_dataset = val_dataset.select(range(min(60, len(val_dataset))))
        print(f"[Otimizacao CPU] Selecionadas {len(train_dataset)} amostras para treino rapido (< 40 min).")

    # 5. Argumentos de Treinamento
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        lr_scheduler_type="cosine",
        warmup_ratio=0.05,
        logging_steps=10,
        save_strategy="epoch",
        evaluation_strategy="epoch",
        report_to="none",
        save_total_limit=1,
        dataloader_num_workers=0,
        use_cpu=(not has_cuda),
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        peft_config=lora_config,
        dataset_text_field="messages",
        max_seq_length=args.max_seq_length,
        tokenizer=tokenizer,
        args=training_args,
    )

    # 6. Executa Treino
    print("\n5/5. Iniciando treinamento da camada de ajustes...")
    trainer.train()

    # 7. Salva a camada de ajustes (LoRA)
    print(f"\nSalvando camada de ajustes em: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)
    trainer.model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    print("\n" + "=" * 65)
    print("[CONCLUIDO COM SUCESSO]")
    print(f"Camada de ajustes salva em: {output_dir}")
    print(f"Arquivos gerados:")
    print(f" - {os.path.join(output_dir, 'adapter_config.json')}")
    print(f" - {os.path.join(output_dir, 'adapter_model.safetensors')}")
    print("\nPara testar a inferencia, execute:")
    print("python3 run_inference.py")
    print("=" * 65)


if __name__ == "__main__":
    main()
