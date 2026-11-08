"""Script de Inferencia para avaliar o modelo com a camada de ajustes (LoRA).

Carrega o modelo base e acopla os adaptadores salvos em `lora_adapters/`.
Executa o diagnóstico nos cenários do desafio (Atendimento e Logística).
Suporta tanto CPU quanto GPU automaticamente.
"""

import argparse
import os
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inferencia com vitAI + LoRA Adapters")
    parser.add_argument(
        "--base_model",
        type=str,
        default="Qwen/Qwen2.5-0.5B-Instruct",
        help="Modelo base",
    )
    parser.add_argument(
        "--adapter_dir",
        type=str,
        default="lora_adapters",
        help="Diretorio com a camada de ajustes LoRA",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    adapter_path = os.path.join(base_dir, args.adapter_dir)

    try:
        import torch
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as e:
        print(f"[ERRO] Faltam bibliotecas: {e}")
        print("Instale com: pip install torch transformers peft")
        sys.exit(1)

    has_cuda = torch.cuda.is_available()
    device = "cuda" if has_cuda else "cpu"
    torch_dtype = torch.float16 if has_cuda else torch.float32

    print("=" * 60)
    print(f"      vitAI - Inferencia com Modelo Ajustado")
    print("=" * 60)
    print(f"Dispositivo: {'GPU NVIDIA' if has_cuda else 'CPU'}")
    print(f"Modelo Base: {args.base_model}")

    print("1/2. Carregando tokenizer e modelo base...")
    tokenizer = AutoTokenizer.from_pretrained(args.base_model, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        device_map=device,
        torch_dtype=torch_dtype,
        trust_remote_code=True,
    )

    if os.path.exists(os.path.join(adapter_path, "adapter_config.json")):
        print(f"2/2. Acoplando camada de ajustes (LoRA) de: {adapter_path}")
        model = PeftModel.from_pretrained(model, adapter_path)
    else:
        print(f"[AVISO] Adaptadores nao encontrados em '{adapter_path}'. Rodando com modelo base.")

    model.eval()

    test_cases = [
        {
            "area": "Atendimento ao Cliente (Sobrecarga de Trabalho)",
            "prompt": (
                "Analise a seguinte área corporativa para o fechamento mensal da NR-1:\n\n"
                "Nome da Área: Atendimento ao Cliente\n"
                "Quadro de Colaboradores: 32 pessoas\n"
                "Variação em Dias de Atestado Médico: +45.0% vs média histórica\n"
                "Variação em Horas Extras: +60.0%\n"
                "Pedidos Voluntários de Demissão: 4 (Média da Empresa: 1.0)\n"
                "Queda na Pesquisa de Clima / Carga de Trabalho: 1.5 pontos (escala 1 a 5)\n"
                "Registros no Canal de Ética e Denúncias: 0\n"
                "Eventos de Contexto Recentes:\n"
                "- 15/08/2026: Implantação de nova meta agressiva de atendimentos por hora (+35%).\n\n"
                "Emita o diagnóstico técnico estruturado contendo: score de risco contínuo (0 a 100), "
                "classificação de severidade (VERDE, AMARELO, VERMELHO), fator psicossocial da NR-1, "
                "síntese da hipótese contextual e a recomendação de deliberação para o PGR."
            ),
        },
        {
            "area": "Logística e Distribuição (Conflito de Liderança)",
            "prompt": (
                "Analise a seguinte área corporativa para o fechamento mensal da NR-1:\n\n"
                "Nome da Área: Logística e Distribuição\n"
                "Quadro de Colaboradores: 28 pessoas\n"
                "Variação em Dias de Atestado Médico: +15.0%\n"
                "Variação em Horas Extras: +5.0%\n"
                "Pedidos Voluntários de Demissão: 5 (Média da Empresa: 1.1)\n"
                "Queda na Pesquisa de Clima / Carga de Trabalho: 1.4 pontos na avaliação de suporte da liderança\n"
                "Registros no Canal de Ética e Denúncias: 0\n"
                "Eventos de Contexto Recentes:\n"
                "- 05/09/2026: Entrada de nova liderança operacional na gestão do armazém.\n\n"
                "Emita o diagnóstico técnico estruturado contendo: score de risco contínuo (0 a 100), "
                "classificação de severidade (VERDE, AMARELO, VERMELHO), fator psicossocial da NR-1, "
                "síntese da hipótese contextual e a recomendação de deliberação para o PGR."
            ),
        },
    ]

    system_prompt = (
        "Você é o vitAI, especialista em governança corporativa de riscos psicossociais no trabalho "
        "e conformidade estrita com a Norma Regulamentadora nº 1 (NR-1) e Portaria MTE nº 1.419/2024."
    )

    for case in test_cases:
        print("\n" + "=" * 60)
        print(f"Diagnostico vitAI: {case['area']}")
        print("=" * 60)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": case["prompt"]},
        ]

        prompt_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(prompt_text, return_tensors="pt").to(device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=400,
                temperature=0.2,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
            )

        new_tokens = outputs[0][inputs["input_ids"].shape[1] :]
        response = tokenizer.decode(new_tokens, skip_special_tokens=True)
        print(response)


if __name__ == "__main__":
    main()
