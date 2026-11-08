"""Ciclo mensal do digital worker.

1. Fechamento: analisa todas as areas e abre cards (motor transparente, sem LLM decidir nivel).
2. Para cada card ABERTO amarelo/vermelho:
   - investiga na base da empresa o que ja existe (programas, canais, planos anteriores, lacunas);
   - prepara uma intervencao na fila do RH, com a primeira tarefa, AGUARDANDO aprovacao;
   - se houver canal de RH configurado, prepara um aviso neutro no Slack (tambem aguarda aprovacao).
3. Revisa a base de conhecimento e devolve as pendencias (vencendo, lacunas, sem canal...).

Idempotente: rodar de novo no mesmo card nao duplica a intervencao (chave por card).
Assedio e casos escalados nunca entram aqui: seguem o fluxo de compliance.
"""

import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import UTC, date, datetime, timedelta
from typing import Any

from sqlalchemy import select

from app.application.contracts.identity import ContextoAutorizado
from app.domain.entities.risk_card import CardStatus
from app.domain.entities.risk_factor import RiskLevel
from app.rh_actions import tables as t
from app.rh_actions.contracts import (
    ActionError,
    PrepareAction,
    PrepareIntervention,
    SlackPayload,
    TaskPayload,
)
from app.rh_actions.service import ActionService

logger = logging.getLogger(__name__)

PRAZO_PRIMEIRA_TAREFA = timedelta(days=7)
LIMITE_OBJETIVO = 1500
NOME_FATOR = {
    "SOBRECARGA_METAS": "sobrecarga e metas",
    "JORNADAS_LONGAS": "jornadas longas",
    "LIDERANCA_CONFLITO": "conflito com a lideranca",
    "ASSEDIO": "assedio",
    "FALTA_CLAREZA_PAPEL": "falta de clareza de papel",
    "FALTA_AUTONOMIA": "falta de autonomia",
    "INSEGURANCA_TRABALHO": "inseguranca no trabalho",
}


def _valor(item: Any) -> str:
    return str(getattr(item, "value", item))


@dataclass
class CardNoCiclo:
    card_id: str
    area_id: str
    area: str
    nivel: str
    fator: str
    resultado: str  # PROPOSTA_PREPARADA | PROPOSTA_JA_EXISTIA | FLUXO_COMPLIANCE | BLOQUEADO
    intervencao_id: str | None = None
    aviso_slack: bool = False
    tem_acao_da_empresa: bool | None = None
    lacunas: list[str] = field(default_factory=list)
    motivo: str | None = None


@dataclass
class ResultadoCiclo:
    executado_em: str
    areas_analisadas: int
    cards_abertos: int
    cards: list[CardNoCiclo]
    pendencias_base: list[dict[str, Any]]

    def como_dict(self) -> dict[str, Any]:
        def camel(nome: str) -> str:
            primeira, *resto = nome.split("_")
            return primeira + "".join(p.title() for p in resto)

        def converter(valor: Any) -> Any:
            if isinstance(valor, dict):
                return {camel(k): converter(v) for k, v in valor.items()}
            if isinstance(valor, list):
                return [converter(v) for v in valor]
            if isinstance(valor, date):
                return valor.isoformat()
            return valor

        return converter(asdict(self))  # type: ignore[no-any-return]


def canal_slack_configurado() -> str | None:
    canais = [c.strip() for c in os.getenv("VYTAI_SLACK_ALLOWED_CHANNELS", "").split(",")]
    return next((c for c in canais if c), None)


def montar_objetivo(card: Any, investigacao: Any | None) -> str:
    """Texto interno da fila (nunca vai ao Slack). Sem dados individuais: so area e fontes."""
    fator = _valor(card.probable_risk_factor)
    partes = [
        f"Card {_valor(card.risk_level)} de {NOME_FATOR.get(fator, fator)} em {card.area_name}, "
        "aberto pelo fechamento do VytAI. Revisar com a lideranca e decidir a acao do PGR."
    ]
    if investigacao is None:
        partes.append("Base de conhecimento indisponivel nesta execucao.")
    else:
        trechos = {t.ref: t for t in investigacao.trechos()}
        if investigacao.acoes_disponiveis:
            nomes = sorted({t.titulo_documento for t in investigacao.acoes_disponiveis})
            partes.append("A empresa ja oferece: " + "; ".join(nomes) + ".")
        if investigacao.planos_anteriores:
            nomes = sorted({t.titulo for t in investigacao.planos_anteriores})
            partes.append("Ja foi tentado antes: " + "; ".join(nomes) + ".")
        if investigacao.lacunas:
            partes.append("Lacunas na base: " + " ".join(investigacao.lacunas))
        if trechos:
            fontes = ", ".join(f"[{ref}] {t.titulo}" for ref, t in list(trechos.items())[:6])
            partes.append("Fontes: " + fontes + ".")
    texto = " ".join(partes)
    return texto if len(texto) <= LIMITE_OBJETIVO else texto[: LIMITE_OBJETIVO - 3] + "..."


def executar_ciclo(
    ctx: ContextoAutorizado,
    container: Any,
    conhecimento: Any | None,
    acoes: ActionService,
    agora: datetime | None = None,
    canal_slack: str | None = None,
) -> ResultadoCiclo:
    agora = agora or datetime.now(UTC)
    resultados = container.run_analysis_uc.execute_all()
    abertos = [
        c
        for c in container.risk_card_repo.list_all()
        if _valor(c.status) == CardStatus.ABERTO.value
        and _valor(c.risk_level) in (RiskLevel.VERMELHO.value, RiskLevel.AMARELO.value)
    ]
    cards: list[CardNoCiclo] = []
    for card in sorted(abertos, key=lambda c: (_valor(c.risk_level) != "VERMELHO", c.area_name)):
        fator = _valor(card.probable_risk_factor)
        item = CardNoCiclo(
            card.id, card.area_id, card.area_name, _valor(card.risk_level), fator, "BLOQUEADO"
        )
        cards.append(item)
        if fator == "ASSEDIO":
            item.resultado, item.motivo = "FLUXO_COMPLIANCE", "Assedio segue o canal de compliance."
            continue
        investigacao = None
        if conhecimento is not None:
            investigacao = conhecimento.assistente.investigar(
                ctx, fator, card.area_name, dia=agora.date()
            )
            item.tem_acao_da_empresa = investigacao.tem_acao_da_empresa
            item.lacunas = list(investigacao.lacunas)
        chave = f"ciclo:{card.id}"
        existente = acoes.session.execute(
            select(t.interventions.c.id).where(
                t.interventions.c.empresa_id == ctx.empresa_id,
                t.interventions.c.idempotency_key == chave,
            )
        ).scalar_one_or_none()
        if existente is not None:
            # Ja proposta num ciclo anterior: nao repreparar (o prazo/objetivo mudariam).
            item.intervencao_id, item.resultado = str(existente), "PROPOSTA_JA_EXISTIA"
            continue
        try:
            intervencao = acoes.prepare_intervention(
                PrepareIntervention(
                    area_id=card.area_id,
                    title=f"Acompanhar {NOME_FATOR.get(fator, fator)} - {card.area_name}"[:160],
                    objective=montar_objetivo(card, investigacao),
                    source_card_id=card.id,
                    first_task=TaskPayload(
                        title=f"Revisar o card de {card.area_name} com a lideranca"[:160],
                        due_at=agora + PRAZO_PRIMEIRA_TAREFA,
                    ),
                ),
                chave,
            )
            item.intervencao_id = str(intervencao["id"])
            item.resultado = "PROPOSTA_PREPARADA"
            if canal_slack:
                acoes.prepare_action(
                    intervencao["id"],
                    PrepareAction(
                        payload=SlackPayload(channel=canal_slack, template="FOLLOW_UP"),
                        not_before=agora,
                    ),
                    f"ciclo-slack:{card.id}",
                )
                item.aviso_slack = True
        except ActionError as erro:
            item.resultado = "FLUXO_COMPLIANCE" if erro.code == "COMPLIANCE_ONLY" else "BLOQUEADO"
            item.motivo = erro.message
            logger.info("Card %s fora da fila: %s", card.id, erro.code)

    pendencias: list[dict[str, Any]] = []
    if conhecimento is not None:
        relatorio = conhecimento.assistente.revisar_base(ctx, agora.date())
        pendencias = [asdict(p) for p in relatorio.pendencias]
    return ResultadoCiclo(
        executado_em=agora.isoformat(timespec="seconds"),
        areas_analisadas=len(resultados),
        cards_abertos=len(abertos),
        cards=cards,
        pendencias_base=pendencias,
    )
