"""Ferramentas do agente: preparar e consultar. Nao aprovar, enviar ou inventar execucao."""

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session
from strands import tool

from app.application.contracts.identity import ContextoAutorizado
from app.rh_actions.contracts import (
    PrepareAction,
    PrepareIntervention,
    SlackPayload,
    TaskPayload,
    digest,
)
from app.rh_actions.service import ActionService, utcnow


def build_rh_tools(ctx: ContextoAutorizado, session_factory: Callable[[], Session]) -> list[Any]:
    @contextmanager
    def service() -> Iterator[ActionService]:
        # Ferramentas podem rodar em threads do Strands: nunca compartilhar a Session do request.
        with session_factory() as session, session.begin():
            session.execute(text("SET LOCAL ROLE vytai_app"))
            session.execute(
                text("SELECT set_config('vytai.empresa_id',:empresa,true)"),
                {"empresa": str(ctx.empresa_id)},
            )
            active = session.execute(
                text(
                    "SELECT 1 FROM empresa_usuario WHERE empresa_id=:empresa AND usuario_id=:user AND ativo AND 'RH'=ANY(papeis)"
                ),
                {"empresa": ctx.empresa_id, "user": ctx.usuario_id},
            ).first()
            if not active:
                raise ValueError("Identidade RH nao autorizada.")
            yield ActionService(session, ctx)

    @tool
    def preparar_intervencao(area_id: str, objetivo: str, prazo_dias: int = 15) -> dict:
        """Prepara proposta e tarefa pendente para revisao do RH. Nao aprova PGR nem executa envios.

        Args:
            area_id: ID de area autorizada com pelo menos cinco pessoas.
            objetivo: Objetivo organizacional da intervencao, sem dados individuais.
            prazo_dias: Prazo de acompanhamento entre 1 e 180 dias.
        """
        if not 1 <= prazo_dias <= 180:
            raise ValueError("Prazo entre 1 e 180 dias.")
        due = (utcnow() + timedelta(days=prazo_dias)).replace(
            hour=12, minute=0, second=0, microsecond=0
        )
        body = PrepareIntervention(
            area_id=area_id,
            title="Acompanhar acao do RH",
            objective=objetivo,
            first_task=TaskPayload(title="Acompanhar intervencao e reunir evidencias", due_at=due),
        )
        key = "agent:" + digest(
            {"actor": str(ctx.usuario_id), "request": body.model_dump(mode="json", by_alias=True)}
        )
        with service() as svc:
            result = svc.prepare_intervention(body, key)
            return {
                "interventionId": str(result["id"]),
                "state": "PENDING_HR_REVIEW",
                "message": "Proposta preparada. O RH deve revisar e aprovar na fila de acoes.",
            }

    @tool
    def consultar_pendencias() -> dict:
        """Lista tarefas abertas e acoes que aguardam aprovacao ou conferencia, apenas desta empresa."""
        with service() as svc:
            result = svc.pending()
            return {
                "actions": [
                    {
                        "id": str(a["id"]),
                        "kind": a["kind"],
                        "status": a["status"],
                        "errorCode": a["error_code"],
                    }
                    for a in result["actions"]
                ],
                "tasks": [
                    {
                        "id": str(t["id"]),
                        "title": t["title"],
                        "dueAt": t["due_at"].isoformat(),
                        "overdue": t["overdue"],
                    }
                    for t in result["tasks"]
                ],
            }

    @tool
    def preparar_comunicacao(intervencao_id: str, canal_slack: str) -> dict:
        """Prepara mensagem neutra de acompanhamento em Slack. Nao envia: exige revisao e aprovacao do RH.

        Args:
            intervencao_id: ID da intervencao autorizada.
            canal_slack: ID do canal de RH; o conector valida allowlist antes de enviar.
        """
        id = UUID(intervencao_id)
        when = utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        body = PrepareAction(payload=SlackPayload(channel=canal_slack), not_before=when)
        key = "agent-msg:" + digest(
            {
                "actor": str(ctx.usuario_id),
                "id": str(id),
                "request": body.model_dump(mode="json", by_alias=True),
            }
        )
        with service() as svc:
            row = svc.prepare_action(id, body, key)
            return {
                "actionId": str(row["id"]),
                "status": row["status"],
                "preview": row["preview"],
                "message": "Ainda nao enviado. Aprovar na fila do RH.",
            }

    @tool
    def preparar_reavaliacao(intervencao_id: str, prazo_dias: int = 60) -> dict:
        """Prepara tarefa de reavaliacao futura; nao afirma melhora nem encerra PGR.

        Args:
            intervencao_id: ID da intervencao.
            prazo_dias: Dias ate a verificacao, entre 15 e 180.
        """
        if not 15 <= prazo_dias <= 180:
            raise ValueError("Prazo entre 15 e 180 dias.")
        due = (utcnow() + timedelta(days=prazo_dias)).replace(
            hour=12, minute=0, second=0, microsecond=0
        )
        body = PrepareAction(
            payload=TaskPayload(
                title="Reavaliar indicadores e evidencias da intervencao",
                due_at=due,
                purpose="REEVALUATION",
            ),
            not_before=due - timedelta(days=prazo_dias),
        )
        key = "agent-reval:" + digest(
            {
                "actor": str(ctx.usuario_id),
                "id": intervencao_id,
                "request": body.model_dump(mode="json", by_alias=True),
            }
        )
        with service() as svc:
            row = svc.prepare_action(UUID(intervencao_id), body, key)
            return {
                "actionId": str(row["id"]),
                "status": row["status"],
                "message": "Reavaliacao proposta; ainda nao executada nem aprovada.",
            }

    return [preparar_intervencao, consultar_pendencias, preparar_comunicacao, preparar_reavaliacao]
