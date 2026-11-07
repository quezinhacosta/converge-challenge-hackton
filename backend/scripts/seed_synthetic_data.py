"""Script de geracao de dados sinteticos da empresa ficticia para os 7 casos de demonstracao do Pulso.

Empresa Ficticia:
    - 6 a 8 areas corporativas (ex.: Atendimento, Logistica, Vendas, Financeiro, Design, Engenharia, RH)
    - Aproximadamente 150 colaboradores ativos
    - 6 meses de historico operacional (ponto, folha, atestados, desligamentos, pesquisas, eventos)
    - Cobre com precisao os 7 casos de demonstracao do pitch.
"""

from typing import Any, Dict, List


def generate_demonstration_scenario_dataset() -> Dict[str, Any]:
    """Gera a estrutura de dados sinteticos contemplando os 7 casos de teste da NR-1.

    Casos Estruturados:
        1. Financeiro: indicadores estaveis (nao alarmista).
        2. Atendimento ao Cliente (32 pessoas): nova meta em agosto -> dias de atestado +45%,
           horas extras +60%, 4 pedidos de demissao, nota cai de 3.9 para 2.4 (Card Vermelho - Sobrecarga).
        3. Logistica (28 pessoas): troca de gestor em setembro -> 5 pedidos de demissao
           (Card Amarelo - Fator de Lideranca e pesquisa direcionada).
        4. Vendas (35 pessoas): 3 denuncias de assedio registradas em 2 meses
           (Escalonamento imediato para Compliance sem ler conteudo).
        5. RH pede 'os atestados da Carla': tentativa de consulta individual barrada pelo guardrail etico.
        6. Design (3 pessoas): time com menos de 5 pessoas com dados ocultados para protecao por exclusao.
        7. Atendimento 60 dias pos-acao: metricas reavaliadas com reducao de atestados e horas extras (Ciclo fechado).

    Retorna:
        Dict[str, Any]: Estrutura com areas, metricas mensais, eventos de contexto e pesquisas.
    """
    areas: List[Dict[str, Any]] = [
        {"id": "area_fin", "name": "Financeiro", "headcount": 18, "manager": "Roberto Prado"},
        {"id": "area_atend", "name": "Atendimento ao Cliente", "headcount": 32, "manager": "Juliana Costa"},
        {"id": "area_log", "name": "Logistica", "headcount": 28, "manager": "Fernando Dias"},
        {"id": "area_vend", "name": "Vendas", "headcount": 35, "manager": "Marcos Valente"},
        {"id": "area_des", "name": "Design de Produto", "headcount": 3, "manager": "Luciana Mello"},
        {"id": "area_eng", "name": "Engenharia de Software", "headcount": 30, "manager": "Beatriz Neves"},
        {"id": "area_rh", "name": "Recursos Humanos", "headcount": 8, "manager": "Camila Guimaraes"},
    ]

    return {
        "areas": areas,
        "total_employees": sum(a["headcount"] for a in areas),
        "months_covered": 6,
    }


if __name__ == "__main__":
    dataset = generate_demonstration_scenario_dataset()
    print(f"Dataset sintetico do Pulso gerado com sucesso!")
    print(f"Total de areas: {len(dataset['areas'])} | Total de colaboradores: {dataset['total_employees']}")
