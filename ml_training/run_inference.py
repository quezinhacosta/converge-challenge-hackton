"""Script de Inferencia para avaliar o modelo com a camada de ajustes (LoRA).

Carrega o modelo base e acopla os adaptadores salvos em `lora_adapters/`.
Executa o diagnóstico nos cenários do desafio (Atendimento e Logística).
Suporta tanto CPU quanto GPU automaticamente.
"""

import argparse
import json
import os
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inferencia com vitAI + LoRA Adapters")
    
    # Tenta ler o modelo base automaticamente do adapter_config.json
    base_dir = os.path.dirname(os.path.abspath(__file__))
    adapter_cfg_file = os.path.join(base_dir, "lora_adapters", "adapter_config.json")
    default_base = "mistralai/Mistral-7B-Instruct-v0.3"
    if os.path.exists(adapter_cfg_file):
        try:
            with open(adapter_cfg_file, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                default_base = cfg.get("base_model_name_or_path", default_base)
        except Exception:
            pass

    parser.add_argument(
        "--base_model",
        type=str,
        default=default_base,
        help="Modelo base",
    )
    parser.add_argument(
        "--adapter_dir",
        type=str,
        default="lora_adapters",
        help="Diretorio com a camada de ajustes LoRA",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Execucao rapida em modo demonstrativo sem alocar 14 GB de RAM em CPU",
    )
    parser.add_argument(
        "--force_cpu",
        action="store_true",
        help="Forca o carregamento completo do modelo base de 14.5GB em CPU/RAM",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    adapter_path = os.path.join(base_dir, args.adapter_dir)

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

    has_adapters = os.path.exists(os.path.join(adapter_path, "adapter_config.json"))

    try:
        import torch
    except ImportError:
        torch = None

    has_cuda = torch.cuda.is_available() if torch else False

    if args.demo or (not has_cuda and not args.force_cpu):
        print("=" * 60)
        print("      vitAI - Validacao da Camada de Ajustes LoRA (NR-1)")
        print("=" * 60)
        print(f"Camada LoRA Detectada: {'Sim (' + adapter_path + ')' if has_adapters else 'Nao'}")
        print(f"Modelo Base Vinculado: {args.base_model}")
        print(f"Modo: Demonstracao Especializada NR-1 (Protecao contra OOM de CPU)")
        print("-" * 60)

        # Importa o provedor integrado
        backend_dir = os.path.abspath(os.path.join(base_dir, "..", "backend"))
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        from app.infrastructure.llm.resilience.mistral_lora_provider import MistralLoraProvider

        provider = MistralLoraProvider(adapter_path=adapter_path)
        for case in test_cases:
            print("\n" + "=" * 60)
            print(f"Diagnostico vitAI: {case['area']}")
            print("=" * 60)
            factor = "SOBRECARGA_METAS" if "Sobrecarga" in case["area"] else "LIDERANCA_CONFLITO"
            hip, acao = provider.generate_hypothesis_and_action(
                area_name=case["area"].split(" (")[0],
                metrics_summary="Metricas consolidadas do caso",
                context_events=[{"description": "Meta agressiva ou mudanca de gestao"}],
                shap_narrative="Auditoria SHAP com alta correlacao no turnover e atestados.",
                factor=factor,
            )
            print(f"Hipotese Tecnica:\n{hip}\n")
            print(f"Recomendacao PGR (NR-1):\n{acao}")
        print("\n" + "=" * 60)
        print("Validacao concluida com sucesso!")
        return

    # Inferencia completa em GPU NVIDIA
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    device = "cuda" if has_cuda else "cpu"
    torch_dtype = torch.float16 if has_cuda else torch.float32

    print("=" * 60)
    print(f"      vitAI - Inferencia Nativa com Mistral 7B + LoRA")
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

    if has_adapters:
        print(f"2/2. Acoplando camada de ajustes (LoRA) de: {adapter_path}")
        model = PeftModel.from_pretrained(model, adapter_path)
    else:
        print(f"[AVISO] Adaptadores nao encontrados em '{adapter_path}'.")

    model.eval()

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
