"""Gerador de dataset sintetico para treinamento de modelo de risco psicossocial (NR-1).

Gera amostras tabulares realistas baseadas nos cenarios da Portaria MTE nº 1.419/2024:
1. Equipes estaveis (Risco Baixo - Verde)
2. Sobrecarga operacional de trabalho (Risco Alto/Critico - Amarelo/Vermelho)
3. Conflitos de lideranca e clima degradado (Risco Alto - Amarelo/Vermelho)
4. Infracoes de compliance / assedio (Risco Critico com isolamento etico)
"""

import csv
import json
import math
import os
import random
from typing import Any, Dict, List


def generate_synthetic_dataset(
    n_samples: int = 1200, seed: int = 42
) -> List[Dict[str, Any]]:
    random.seed(seed)
    records: List[Dict[str, Any]] = []

    # Proporcao de cenarios para diversidade representativa
    # 40% Estavel, 25% Sobrecarga, 25% Clima/Lideranca, 10% Assedio/Compliance
    for i in range(n_samples):
        r = random.random()

        if r < 0.40:
            # 1. Equipe Estavel (Normal)
            var_atestados = round(random.gauss(1.0, 4.0), 1)
            var_he = round(random.gauss(0.0, 3.5), 1)
            media_demissoes = round(random.uniform(1.0, 1.5), 1)
            demissoes = 0 if random.random() < 0.7 else 1
            queda_clima = round(max(-0.5, random.gauss(0.0, 0.2)), 2)
            denuncias = 0

            score = max(
                5.0,
                min(
                    28.0, 12.0 + var_atestados * 0.4 + var_he * 0.3 + queda_clima * 10.0
                ),
            )
            probable_factor = "ESTABILIDADE"
            level = "VERDE"

        elif r < 0.65:
            # 2. Sobrecarga de Trabalho (Excesso de jornada + Atestados medicos)
            var_atestados = round(random.uniform(20.0, 65.0), 1)
            var_he = round(random.uniform(15.0, 50.0), 1)
            media_demissoes = round(random.uniform(1.0, 2.0), 1)
            demissoes = random.choice([1, 2, 3])
            queda_clima = round(random.uniform(0.3, 1.1), 2)
            denuncias = 0 if random.random() < 0.85 else 1

            # Calculo continuo
            raw_score = (
                45.0 + (var_atestados * 0.45) + (var_he * 0.40) + (queda_clima * 12.0)
            )
            score = round(min(98.0, max(52.0, raw_score)), 1)
            probable_factor = "SOBRECARGA_TRABALHO"
            level = "VERMELHO" if score >= 70.0 else "AMARELO"

        elif r < 0.90:
            # 3. Conflito de Lideranca / Degradação de Clima e Turnover
            var_atestados = round(random.uniform(8.0, 28.0), 1)
            var_he = round(random.uniform(-5.0, 15.0), 1)
            media_demissoes = round(random.uniform(0.8, 1.4), 1)
            demissoes = random.choice(
                [3, 4, 5, 6]
            )  # Pico atipico de saidas voluntarias
            queda_clima = round(random.uniform(0.8, 2.2), 2)  # Queda brusca na nota
            denuncias = random.choice([0, 1])

            turnover_ratio = demissoes / max(0.5, media_demissoes)
            raw_score = (
                40.0
                + (queda_clima * 18.0)
                + (turnover_ratio * 7.0)
                + (var_atestados * 0.25)
            )
            score = round(min(96.0, max(50.0, raw_score)), 1)
            probable_factor = "CONFLITO_LIDERANCA"
            level = "VERMELHO" if score >= 70.0 else "AMARELO"

        else:
            # 4. Denuncias Graves / Assedio (Canal de Compliance)
            var_atestados = round(random.uniform(5.0, 35.0), 1)
            var_he = round(random.uniform(-10.0, 20.0), 1)
            media_demissoes = round(random.uniform(1.0, 1.8), 1)
            demissoes = random.choice([1, 2, 4])
            queda_clima = round(random.uniform(0.5, 1.8), 2)
            denuncias = random.choice([3, 4, 5, 6])  # Multiplas denuncias graves

            raw_score = 75.0 + (denuncias * 4.0) + (queda_clima * 5.0)
            score = round(min(99.0, max(75.0, raw_score)), 1)
            probable_factor = "ASSEDIO_OU_VIOLENCIA"
            level = "VERMELHO"

        # Adiciona ruido estocastico sutil para simular dados empiricos reais
        score_com_ruido = round(max(0.0, min(100.0, score + random.gauss(0.0, 1.2))), 1)

        records.append(
            {
                "id": f"sample_{i + 1:04d}",
                "variacao_dias_atestado_pct": var_atestados,
                "variacao_horas_extras_pct": var_he,
                "pedidos_demissao": demissoes,
                "media_empresa_pedidos_demissao": media_demissoes,
                "queda_nota_clima": queda_clima,
                "denuncias_compliance": denuncias,
                "risk_score": score_com_ruido,
                "risk_level": level,
                "probable_factor": probable_factor,
            }
        )

    return records


def save_dataset(records: List[Dict[str, Any]], output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)

    csv_path = os.path.join(output_dir, "dataset_nr1.csv")
    json_path = os.path.join(output_dir, "dataset_nr1.json")

    fieldnames = [
        "id",
        "variacao_dias_atestado_pct",
        "variacao_horas_extras_pct",
        "pedidos_demissao",
        "media_empresa_pedidos_demissao",
        "queda_nota_clima",
        "denuncias_compliance",
        "risk_score",
        "risk_level",
        "probable_factor",
    ]

    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    with open(json_path, mode="w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"Dataset gerado com sucesso: {len(records)} amostras.")
    print(f"Arquivos salvos em:\n - {csv_path}\n - {json_path}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data = generate_synthetic_dataset(n_samples=1500)
    save_dataset(data, base_dir)
