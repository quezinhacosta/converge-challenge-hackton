"""Validador de inferencia do motor treinado sobre os cenarios oficiais de demonstracao."""

import os
import sys

# Garante path correto
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from trained_engine import TrainedRiskEngine


def run_tests() -> None:
    print("Iniciando validacao do motor treinado...")
    engine = TrainedRiskEngine()

    scenarios = [
        {
            "name": "Cenario 1 - Financeiro (Estabilidade)",
            "params": {
                "variacao_dias_atestado_pct": 2.0,
                "variacao_horas_extras_pct": 1.5,
                "pedidos_demissao": 0,
                "media_empresa_pedidos_demissao": 1.2,
                "queda_nota_clima": 0.1,
                "denuncias_compliance": 0,
            },
            "expected_level": "VERDE",
        },
        {
            "name": "Cenario 2 - Atendimento ao Cliente (Sobrecarga de Trabalho)",
            "params": {
                "variacao_dias_atestado_pct": 42.0,
                "variacao_horas_extras_pct": 35.0,
                "pedidos_demissao": 2,
                "media_empresa_pedidos_demissao": 1.0,
                "queda_nota_clima": 0.6,
                "denuncias_compliance": 0,
            },
            "expected_level": "VERMELHO",
        },
        {
            "name": "Cenario 3 - Logistica (Conflito de Lideranca / Troca de Gestao)",
            "params": {
                "variacao_dias_atestado_pct": 18.0,
                "variacao_horas_extras_pct": 8.0,
                "pedidos_demissao": 4,
                "media_empresa_pedidos_demissao": 1.1,
                "queda_nota_clima": 1.4,
                "denuncias_compliance": 0,
            },
            "expected_level": "VERMELHO",
        },
        {
            "name": "Cenario 4 - Vendas (Denuncias Graves de Compliance)",
            "params": {
                "variacao_dias_atestado_pct": 10.0,
                "variacao_horas_extras_pct": 5.0,
                "pedidos_demissao": 2,
                "media_empresa_pedidos_demissao": 1.0,
                "queda_nota_clima": 0.9,
                "denuncias_compliance": 3,
            },
            "expected_level": "VERMELHO",
        },
    ]

    for sc in scenarios:
        print(f"\n==========================================")
        print(f"Executando: {sc['name']}")
        res = engine.predict(**sc["params"])  # type: ignore[arg-type]
        print(f"Score Predito: {res.risk_score}/100")
        print(f"Nivel de Risco: {res.risk_level.value}")
        print(f"Fator Provavel: {res.probable_factor.value}")
        print("Decomposicao SHAP:")
        for shap in res.shap_breakdown[:3]:
            print(
                f"  - {shap.display_name}: {shap.contribution_pct}% ({shap.direction})"
            )

        assert res.risk_level.value == sc["expected_level"], (
            f"Esperado {sc['expected_level']}, obtido {res.risk_level.value}"
        )
        print("Status: Aprovado!")

    print("\nTodos os 4 cenarios validados com sucesso no motor treinado!")


if __name__ == "__main__":
    run_tests()
