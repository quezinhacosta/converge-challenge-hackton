"""Fidelidade do chat: casos reais observados ao vivo com o Qwen na Featherless (2026-11-08)."""

import json

from app.infrastructure.llm.fidelidade_chat import (
    FRASE_SEM_REGISTRO,
    RESPOSTA_SEM_FONTE,
    aplicar_fidelidade,
    resultados_de_ferramentas,
)

SINAIS_ATENDIMENTO = {
    "area_name": "Atendimento ao Cliente",
    "headcount": 32,
    "variacao_dias_atestado_pct": 34.5,
    "variacao_horas_extras_pct": 50.0,
    "pedidos_demissao_periodo": 4,
    "media_empresa_pedidos_demissao": 1.0,
    "nota_carga_trabalho_atual": 2.4,
    "nota_carga_trabalho_anterior": 3.0,
    "eventos": ["15/08/2026: nova meta de atendimentos por hora (+35%)."],
}
MENSAGENS = [
    {"role": "user", "content": [{"text": "Como esta o Atendimento?"}]},
    {"role": "assistant", "content": [{"toolUse": {"name": "sinais_da_area", "input": {}}}]},
    {
        "role": "user",
        "content": [
            {
                "toolResult": {
                    "status": "success",
                    "content": [{"text": json.dumps(SINAIS_ATENDIMENTO)}],
                }
            }
        ],
    },
    {
        "role": "user",
        "content": [{"toolResult": {"status": "error", "content": [{"text": "headcount 99"}]}}],
    },
]


def test_numeros_inventados_sao_removidos_e_os_da_ferramenta_ficam() -> None:
    evid = resultados_de_ferramentas(MENSAGENS)
    resposta = (
        "A area de Atendimento ao Cliente tem 12 pessoas. "
        "As horas extras subiram 50% e os atestados 34,5%. "
        "A nota de carga caiu de 3,0 para 2,4. "
        "Recomendo preparar uma intervencao."
    )
    final = aplicar_fidelidade(resposta, evid)
    assert "12 pessoas" not in final
    assert "50%" in final and "34,5%" in final and "3,0 para 2,4" in final
    assert "Recomendo preparar" in final


def test_resultado_com_erro_nao_vale_como_fonte() -> None:
    final = aplicar_fidelidade("A area tem 99 pessoas.", resultados_de_ferramentas(MENSAGENS))
    assert final == RESPOSTA_SEM_FONTE


def test_ausencia_vira_nao_encontrei_na_base() -> None:
    final = aplicar_fidelidade(
        "A area tem 32 pessoas. A empresa nao possui canais especificos de apoio para "
        "sobrecarga. Tambem nao ha programa de apoio psicologico.",
        resultados_de_ferramentas(MENSAGENS),
    )
    assert "32 pessoas" in final
    assert "nao possui canais" not in final and "nao ha programa" not in final
    assert final.count(FRASE_SEM_REGISTRO) == 1


def test_nr1_citacoes_datas_e_pergunta_nao_sao_numeros_sem_fonte() -> None:
    final = aplicar_fidelidade(
        "Pela NR-1, o Programa Cuidar oferece apoio [C1]. A meta mudou em 15/08/2026. "
        "Considere os ultimos 6 meses.",
        resultados_de_ferramentas(MENSAGENS),
        pergunta="Como esta a area nos ultimos 6 meses?",
    )
    assert "NR-1" in final and "[C1]" in final and "15/08/2026" in final and "6 meses" in final


def test_sem_ferramenta_e_com_numero_cai_na_resposta_segura() -> None:
    assert aplicar_fidelidade("A Logistica tem 28 pessoas e 3 afastamentos.", "") == (
        RESPOSTA_SEM_FONTE
    )
