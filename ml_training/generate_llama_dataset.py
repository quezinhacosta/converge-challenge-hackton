"""Gerador de dataset de instrucao para fine-tuning do Llama-3.1-8B-Instruct.

Formata as amostras operacionais no padrao oficial de mensagens do Llama 3.1:
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
...
<|start_header_id|>user<|end_header_id|>
...
<|start_header_id|>assistant<|end_header_id|>

Gera arquivos `train_dataset.jsonl` e `val_dataset.jsonl` para treinamento com TRL / SFTTrainer.
"""

import json
import os
import random
from typing import Any, Dict, List


SYSTEM_PROMPT = (
    "Você é o vitAI, especialista em governança corporativa de riscos psicossociais no trabalho "
    "e conformidade estrita com a Norma Regulamentadora nº 1 (NR-1) e Portaria MTE nº 1.419/2024. "
    "Sua função é analisar indicadores operacionais de áreas corporativas (atestados, horas extras, "
    "turnover voluntário, pesquisas de clima e denúncias de compliance), correlacioná-los a eventos "
    "de contexto recentes e emitir um parecer técnico fundamentado com diagnóstico de severidade, "
    "fator de risco predominante, hipótese contextual causal e proposta de plano de ação preventivo "
    "para inclusão ou rejeição no inventário do PGR (Programa de Gerenciamento de Riscos)."
)


def create_instruction_sample(
    area_name: str,
    headcount: int,
    var_atestados: float,
    var_he: float,
    demissoes: int,
    media_demissoes: float,
    queda_clima: float,
    denuncias: int,
    eventos: List[str],
    scenario_type: str,
) -> Dict[str, Any]:
    # Formata a mensagem do usuario
    user_prompt = (
        f"Analise a seguinte área corporativa para o fechamento mensal da NR-1:\n\n"
        f"Nome da Área: {area_name}\n"
        f"Quadro de Colaboradores (Headcount): {headcount} pessoas\n"
        f"Variação em Dias de Atestado Médico: {var_atestados:+.1f}% vs média histórica\n"
        f"Variação em Horas Extras: {var_he:+.1f}%\n"
        f"Pedidos Voluntários de Demissão: {demissoes} (Média da Empresa: {media_demissoes:.1f})\n"
        f"Queda na Pesquisa de Clima / Carga de Trabalho: {queda_clima:.1f} pontos (escala 1 a 5)\n"
        f"Registros no Canal de Ética e Denúncias: {denuncias}\n"
    )

    if eventos:
        user_prompt += "Eventos de Contexto Recentes:\n"
        for evt in eventos:
            user_prompt += f"- {evt}\n"
    else:
        user_prompt += "Eventos de Contexto Recentes: Nenhum evento atípico registrado no período.\n"

    user_prompt += (
        "\nEmita o diagnóstico técnico estruturado contendo: score de risco contínuo (0 a 100), "
        "classificação de severidade (VERDE, AMARELO, VERMELHO), fator psicossocial da NR-1, "
        "síntese da hipótese contextual e a recomendação de deliberação para o PGR."
    )

    # Formata a resposta do assistente baseada no cenario
    if scenario_type == "ESTAVEL":
        risk_score = round(random.uniform(8.0, 24.0), 1)
        risk_level = "VERDE"
        fator = "ESTAVEL_SEM_FATOR"
        hipotese = (
            f"A área {area_name} apresenta indicadores operacionais dentro dos limites normativos de variabilidade. "
            "A taxa de afastamentos médicos e a demanda de jornada suplementar estão controladas, sem correlações "
            "de sobrecarga ou instabilidade de gestão. Não há indícios de riscos psicossociais ativos."
        )
        plano = (
            "Manter o monitoramento contínuo de rotina sem necessidade de abertura de Card de Risco "
            "ou intervenção no inventário do PGR neste ciclo."
        )
        pgr_inclusao = False

    elif scenario_type == "SOBRECARGA":
        risk_score = round(random.uniform(75.0, 94.0), 1)
        risk_level = "VERMELHO"
        fator = "SOBRECARGA_METAS"
        hipotese = (
            f"Evidenciada correlação temporal direta entre a alta de {var_he:+.1f}% em horas extras "
            f"e o aumento de {var_atestados:+.1f}% nos dias de atestado na área {area_name}. "
            "Os temas da pesquisa pulso indicam esgotamento por metas desproporcionais e ausência de pausas compensatórias, "
            "caracterizando risco ergonômico e psicossocial iminente conforme o Item 1.5.4 da NR-1."
        )
        plano = (
            "1. Revisão e repactuação imediata de metas com a liderança operacional mediada pelo RH.\n"
            "2. Conversas de escuta com a equipe para readequação de escalas e pausas.\n"
            "3. Aprovação e inclusão obrigatória no Plano de Ação do PGR sob a NR-1 com reavaliação em 60 dias."
        )
        pgr_inclusao = True

    elif scenario_type == "LIDERANCA":
        risk_score = round(random.uniform(55.0, 69.0), 1)
        risk_level = "AMARELO"
        fator = "LIDERANCA_CONFLITO"
        hipotese = (
            f"A área {area_name} registrou {demissoes} pedidos voluntários de demissão (taxa atípica frente à média corporativa de {media_demissoes:.1f}), "
            f"concomitante a uma queda de {queda_clima:.1f} pontos na avaliação de suporte da liderança. "
            "O pico temporal coincide com a recente transição de comando operacional, sinalizando fricção na gestão e desalinhamento comunicacional."
        )
        plano = (
            "1. Disparo de pesquisa de pulso direcionada anônima sobre clima e relação com a nova gestão.\n"
            "2. Sessão de mediação e alinhamento do RH com a liderança do setor.\n"
            "3. Manter card em observação preventiva antes de deliberação definitiva de inserção no PGR."
        )
        pgr_inclusao = False

    elif scenario_type == "ASSEDIO":
        risk_score = round(random.uniform(85.0, 98.0), 1)
        risk_level = "VERMELHO"
        fator = "ASSEDIO"
        hipotese = (
            f"Identificada concentração crítica de {denuncias} registros formais no Canal de Ética e Compliance da área {area_name}. "
            "Por imperativo legal e proteção às vítimas, condutas de assédio moral ou sexual não devem ser tratadas como mero "
            "desvio de processo no inventário geral do PGR, exigindo escalonamento imediato ao Comitê de Conduta com sigilo estrito."
        )
        plano = (
            "1. Escalonamento urgente ao Comitê de Ética e Compliance independente.\n"
            "2. Não inserção no inventário público do PGR para preservação probatória e vedação de retaliação (Protocolo de Blindagem Ética).\n"
            "3. Disponibilização de suporte psicológico externo neutro aos membros da equipe."
        )
        pgr_inclusao = False

    else:
        # LGPD quórum reduzido (< 5)
        risk_score = 0.0
        risk_level = "VERDE"
        fator = "ESTAVEL_SEM_FATOR"
        hipotese = (
            f"A área {area_name} possui apenas {headcount} colaboradores (quórum inferior a 5 pessoas). "
            "Em cumprimento aos princípios de necessidade e não-discriminação da LGPD e diretrizes de anonimização da NR-1, "
            "a análise analítica individualizada é legalmente bloqueada para evitar a reidentificação de colaboradores."
        )
        plano = (
            "Consolidar as métricas na diretoria organizacional de nível superior. Acompanhamento exclusivo via Medicina do Trabalho."
        )
        pgr_inclusao = False

    response_json = {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "probable_factor": fator,
        "hipotese_contextual": hipotese,
        "plano_acao_recomendado": plano,
        "inclusao_pgr_indicada": pgr_inclusao,
    }

    assistant_reply = json.dumps(response_json, indent=2, ensure_ascii=False)

    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": assistant_reply},
        ]
    }


def generate_full_dataset(n_samples: int = 1000, seed: int = 42) -> List[Dict[str, Any]]:
    random.seed(seed)
    areas_pool = [
        ("Atendimento ao Cliente", 32),
        ("Logística e Distribuição", 28),
        ("Vendas B2B", 35),
        ("Financeiro e Controladoria", 18),
        ("Engenharia de Software", 30),
        ("Recursos Humanos", 14),
        ("Marketing e Growth", 16),
        ("Operações de Armazém", 42),
        ("Sucesso do Cliente (CS)", 22),
        ("Design de Produto", 3),  # Quorum pequeno
    ]

    dataset: List[Dict[str, Any]] = []

    for i in range(n_samples):
        area_name, base_hc = random.choice(areas_pool)

        if base_hc < 5:
            # Quorum pequeno
            sample = create_instruction_sample(
                area_name=area_name,
                headcount=base_hc,
                var_atestados=round(random.uniform(0.0, 10.0), 1),
                var_he=round(random.uniform(0.0, 5.0), 1),
                demissoes=0,
                media_demissoes=1.0,
                queda_clima=0.0,
                denuncias=0,
                eventos=[],
                scenario_type="LGPD_PEQUENO",
            )
            dataset.append(sample)
            continue

        r = random.random()
        if r < 0.40:
            # Estavel
            sample = create_instruction_sample(
                area_name=area_name,
                headcount=base_hc,
                var_atestados=round(random.gauss(1.0, 4.0), 1),
                var_he=round(random.gauss(0.0, 3.5), 1),
                demissoes=0 if random.random() < 0.75 else 1,
                media_demissoes=round(random.uniform(0.8, 1.4), 1),
                queda_clima=round(max(0.0, random.gauss(0.1, 0.2)), 1),
                denuncias=0,
                eventos=[],
                scenario_type="ESTAVEL",
            )
        elif r < 0.65:
            # Sobrecarga
            eventos = [
                f"{random.randint(1, 28):02d}/09/2026: Implantação de nova meta agressiva de produtividade (+30%).",
                f"{random.randint(1, 28):02d}/10/2026: Entrada de novo grande cliente contratante sem ampliação de equipe.",
            ]
            sample = create_instruction_sample(
                area_name=area_name,
                headcount=base_hc,
                var_atestados=round(random.uniform(32.0, 68.0), 1),
                var_he=round(random.uniform(35.0, 75.0), 1),
                demissoes=random.choice([2, 3, 4]),
                media_demissoes=round(random.uniform(1.0, 1.5), 1),
                queda_clima=round(random.uniform(1.0, 2.2), 1),
                denuncias=0 if random.random() < 0.85 else 1,
                eventos=eventos[: random.randint(1, 2)],
                scenario_type="SOBRECARGA",
            )
        elif r < 0.88:
            # Conflito lideranca
            eventos = [
                f"{random.randint(1, 28):02d}/09/2026: Mudança de liderança operacional e troca do gestor do setor.",
                f"{random.randint(1, 28):02d}/10/2026: Alteração unilateral nas escalas de trabalho do armazém/time.",
            ]
            sample = create_instruction_sample(
                area_name=area_name,
                headcount=base_hc,
                var_atestados=round(random.uniform(8.0, 26.0), 1),
                var_he=round(random.uniform(0.0, 15.0), 1),
                demissoes=random.choice([4, 5, 6]),
                media_demissoes=round(random.uniform(0.9, 1.3), 1),
                queda_clima=round(random.uniform(1.2, 2.5), 1),
                denuncias=0,
                eventos=eventos[: random.randint(1, 2)],
                scenario_type="LIDERANCA",
            )
        else:
            # Assedio / compliance
            eventos = [
                f"{random.randint(1, 28):02d}/10/2026: Relato formal encaminhado à ouvidoria com alegações de assédio moral.",
            ]
            sample = create_instruction_sample(
                area_name=area_name,
                headcount=base_hc,
                var_atestados=round(random.uniform(10.0, 35.0), 1),
                var_he=round(random.uniform(-5.0, 15.0), 1),
                demissoes=random.choice([1, 2, 3]),
                media_demissoes=round(random.uniform(1.0, 1.6), 1),
                queda_clima=round(random.uniform(0.6, 1.8), 1),
                denuncias=random.choice([3, 4, 5]),
                eventos=eventos,
                scenario_type="ASSEDIO",
            )

        dataset.append(sample)

    return dataset


def save_jsonl(data: List[Dict[str, Any]], filepath: str) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        for row in data:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    samples = generate_full_dataset(n_samples=1200)

    # 85% treino, 15% validacao
    split_idx = int(len(samples) * 0.85)
    train_data = samples[:split_idx]
    val_data = samples[split_idx:]

    train_path = os.path.join(base_dir, "train_dataset.jsonl")
    val_path = os.path.join(base_dir, "val_dataset.jsonl")

    save_jsonl(train_data, train_path)
    save_jsonl(val_data, val_path)

    print(f"Dataset de instrucao Llama 3.1 gerado:")
    print(f" - Treino: {len(train_data)} amostras em {train_path}")
    print(f" - Validacao: {len(val_data)} amostras em {val_path}")
