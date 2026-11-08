"""API operacional do RH. Aprovacao apenas pela sessao humana autenticada."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from pydantic.alias_generators import to_camel
from sqlalchemy.orm import Session

from app.application.contracts.identity import ContextoAutorizado
from app.presentation.security import request_session, require_authorized_context
from app.rh_actions.connectors import Connectors, ConnectorSettings
from app.rh_actions.contracts import (
    ActionError,
    ApproveAction,
    PrepareAction,
    PrepareIntervention,
    ReconcileAction,
    RecordEvidence,
)
from app.rh_actions.service import ActionService

router = APIRouter()


def service(
    ctx: ContextoAutorizado = Depends(require_authorized_context),
    session: Session = Depends(request_session, scope="function"),
) -> ActionService:
    return ActionService(session, ctx)


def key(value: str = Header(alias="Idempotency-Key", min_length=8, max_length=128)) -> str:
    return value


def view(value: Any) -> Any:
    if isinstance(value, dict):
        return {to_camel(k): view(v) for k, v in value.items()}
    if isinstance(value, list):
        return [view(v) for v in value]
    return value


@router.get("/intervencoes")
def list_interventions(svc: ActionService = Depends(service, scope="function")) -> Any:
    return view(svc.list_interventions())


@router.post("/intervencoes", status_code=201)
def prepare_intervention(
    body: PrepareIntervention,
    idempotency: str = Depends(key),
    svc: ActionService = Depends(service, scope="function"),
) -> Any:
    return view(svc.prepare_intervention(body, idempotency))


@router.get("/intervencoes/{id}")
def get_intervention(id: UUID, svc: ActionService = Depends(service, scope="function")) -> Any:
    return view(svc.intervention(id))


@router.get("/intervencoes/{id}/historico")
def history(id: UUID, svc: ActionService = Depends(service, scope="function")) -> Any:
    return view(svc.history(id))


@router.post("/intervencoes/{id}/acoes", status_code=201)
def prepare_action(
    id: UUID,
    body: PrepareAction,
    idempotency: str = Depends(key),
    svc: ActionService = Depends(service, scope="function"),
) -> Any:
    return view(svc.prepare_action(id, body, idempotency))


@router.get("/acoes/{id}")
def get_action(id: UUID, svc: ActionService = Depends(service, scope="function")) -> Any:
    return view(svc.action(id))


@router.post("/acoes/{id}/aprovar")
def approve_action(
    id: UUID, body: ApproveAction, svc: ActionService = Depends(service, scope="function")
) -> Any:
    return view(svc.approve(id, body.expected_digest))


@router.post("/acoes/{id}/cancelar")
def cancel_action(id: UUID, svc: ActionService = Depends(service, scope="function")) -> Any:
    return view(svc.cancel(id))


@router.post("/acoes/{id}/tentar-novamente")
def retry_action(id: UUID, svc: ActionService = Depends(service, scope="function")) -> Any:
    return view(svc.retry(id))


@router.post("/acoes/{id}/solicitar-revisao")
def review_action(id: UUID, svc: ActionService = Depends(service, scope="function")) -> Any:
    return view(svc.request_review(id))


@router.post("/acoes/{id}/reconciliar")
def reconcile_action(
    id: UUID, body: ReconcileAction, svc: ActionService = Depends(service, scope="function")
) -> Any:
    return view(svc.reconcile(id, body))


@router.get("/pendencias")
def pending(svc: ActionService = Depends(service, scope="function")) -> Any:
    return view(svc.pending())


@router.post("/tarefas/{id}/evidencias", status_code=201)
def record_evidence(
    id: UUID, body: RecordEvidence, svc: ActionService = Depends(service, scope="function")
) -> Any:
    return view(svc.record_evidence(id, body))


@router.post("/tarefas/{id}/concluir")
def complete_task(id: UUID, svc: ActionService = Depends(service, scope="function")) -> Any:
    return view(svc.complete_task(id))


@router.post("/tarefas/{id}/cancelar")
def cancel_task(id: UUID, svc: ActionService = Depends(service, scope="function")) -> Any:
    return view(svc.cancel_task(id))


@router.get("/conectores")
def connectors(ctx: ContextoAutorizado = Depends(require_authorized_context)) -> Any:
    if "RH" not in ctx.papeis:
        raise ActionError(403, "RH_REQUIRED", "Apenas o RH pode consultar os conectores.")
    client = Connectors(ConnectorSettings.from_env())
    try:
        return client.readiness(ctx.empresa_id)
    finally:
        client.close()
