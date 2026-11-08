"""Guarda de regressao da avaliacao do RAG (deterministica, sem rede).

Linha de base registrada em 2026-11-08 (rag-eval-v1):
- dev (25): acerto 1.0, top1 1.0, abstencao 0.857 (falha conhecida: d12, sobreposicao lexical
  "trabalho/semana" sem o termo central "remoto"), vazamentos 0, validacao adversaria 1.0.
- validacao (15, congelado): acerto 1.0, abstencao 1.0, vazamentos 0.
Mudou a recuperacao? Rode `python -m tests.eval.rag.avaliacao --split todos` e atualize aqui.
"""

import pytest

from tests.eval.rag.avaliacao import avaliar, carregar_perguntas, hash_split
from tests.eval.rag.corpus import CORPUS

# Nao edite as perguntas de validacao: crie novas no dev. Mudanca aqui exige justificativa.
HASH_VALIDACAO_CONGELADO = "be89bf0e3b39fb7bda882803c18e432628b5305d7162f9361ba48c8cbf37a234"


def test_conjunto_de_validacao_esta_congelado() -> None:
    assert hash_split("validacao") == HASH_VALIDACAO_CONGELADO


def test_perguntas_referenciam_documentos_do_corpus() -> None:
    chaves = {d.chave for d in CORPUS}
    perguntas = carregar_perguntas()
    assert len({p.id for p in perguntas}) == len(perguntas)
    for p in perguntas:
        assert set(p.esperados) | set(p.proibidos) <= chaves, p.id
    assert sum(p.split == "dev" for p in perguntas) == 25
    assert sum(p.split == "validacao" for p in perguntas) == 15


@pytest.mark.parametrize(
    ("split", "acerto_min", "abstencao_min"), [("dev", 0.9, 0.8), ("validacao", 0.9, 0.9)]
)
def test_metricas_nao_regridem(split: str, acerto_min: float, abstencao_min: float) -> None:
    m = avaliar(split)["metricas"]
    # Criticos: tolerancia zero.
    assert m["vazamentos"] == 0, m["falhas"]
    assert m["injecao_nao_marcada"] == 0, m["falhas"]
    assert m["validacao_adversaria"] == 1.0, m["falhas"]
    # Qualidade: piso da linha de base.
    assert m["acerto_recuperacao"] >= acerto_min, m["falhas"]
    assert m["abstencao_correta"] >= abstencao_min, m["falhas"]
