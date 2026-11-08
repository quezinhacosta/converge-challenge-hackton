"""Executa o ciclo do digital worker fora do servidor web (agendador / cron do Render).

    python -m app.digital_worker --once

Usa o mesmo principal de servico do worker de acoes (VYTAI_WORKER_EMPRESA_ID e
VYTAI_WORKER_ACTOR_ID, com vinculo RH ativo). Uma transacao por execucao, com RLS.
"""

import argparse
import json
import logging
import os
import sys
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.application.contracts.identity import ContextoAutorizado
from app.digital_worker.ciclo import canal_slack_configurado, executar_ciclo
from app.infrastructure.persistence.database import get_engine
from app.infrastructure.persistence.repositories import RepositoryBundle
from app.knowledge.integration import criar_servicos_documentais
from app.presentation.deps import PulsoAppContainer
from app.rh_actions.service import ActionService


def main() -> int:
    parser = argparse.ArgumentParser(description="Ciclo do digital worker VytAI")
    parser.add_argument("--once", action="store_true", help="executa um ciclo e encerra")
    args = parser.parse_args()
    if not args.once:
        parser.error("Use --once (o agendamento fica no cron/agendador da plataforma).")
    empresa = os.getenv("VYTAI_WORKER_EMPRESA_ID", "")
    ator = os.getenv("VYTAI_WORKER_ACTOR_ID", "")
    if not empresa or not ator:
        parser.error("Configure VYTAI_WORKER_EMPRESA_ID e VYTAI_WORKER_ACTOR_ID.")
    logging.basicConfig(level=logging.INFO)
    ctx = ContextoAutorizado(
        UUID(empresa), UUID(ator), frozenset({"RH"}), frozenset({"RH"}), f"ciclo-{uuid4()}"
    )
    with Session(get_engine()) as session, session.begin():
        session.execute(
            text("SELECT set_config('vytai.empresa_id', :empresa, true)"),
            {"empresa": str(ctx.empresa_id)},
        )
        conhecimento = criar_servicos_documentais(ctx, session)
        container = PulsoAppContainer(
            RepositoryBundle(session, ctx.empresa_id),
            seed=False,
            context=ctx,
            session=session,
            knowledge=conhecimento,
        )
        resultado = executar_ciclo(
            ctx,
            container,
            conhecimento,
            ActionService(session, ctx),
            canal_slack=canal_slack_configurado(),
        )
    json.dump(resultado.como_dict(), sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
