"""Teste ao vivo dos agentes Strands na Featherless (usa backend/.env).

Uso, a partir da pasta backend:  python -m scripts.smoke_strands
"""

import time

from app.application.dtos.chat_dto import ChatQueryRequestDTO
from app.presentation.deps import PulsoAppContainer


def main() -> None:
    container = PulsoAppContainer()
    provider = container.llm_provider
    print(f"Provedor: {provider.name} | disponivel: {provider.is_available()}")

    start = time.perf_counter()
    analysis = container.analyze_risks_uc.execute("area_atend")
    print(f"\n[Atendimento] nivel={analysis['risk_level']} fator={analysis['factor']}")
    print(f"Hipotese: {analysis['evidence_summary']}")
    print(f"Acao: {analysis['suggested_action']}")
    print(f"Execucao: {analysis.get('ai_execution_metadata')}")
    print(f"Tempo: {time.perf_counter() - start:.1f}s")

    for question in ["Como esta o time de Logistica?", "E o time de Design?"]:
        start = time.perf_counter()
        reply = container.chat_uc.execute(
            ChatQueryRequestDTO(user_id="rh_01", user_name="RH", query_text=question)
        )
        print(f"\n[Chat] {question}\n{reply.reply_text}\n({time.perf_counter() - start:.1f}s)")


if __name__ == "__main__":
    main()
