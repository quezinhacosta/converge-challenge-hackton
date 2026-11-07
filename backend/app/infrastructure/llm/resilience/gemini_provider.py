"""Provedor Primario de IA Generativa via Google Gemini API."""

import importlib
import os
from typing import Any, Dict, List, Optional, Tuple
from app.infrastructure.llm.resilience.interfaces import LLMProviderProtocol


class GeminiProvider(LLMProviderProtocol):
    """Provedor primario de linguagem natural conectando a API do Google Gemini."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-pro") -> None:
        """Inicializa o cliente do Gemini."""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name

    @property
    def name(self) -> str:
        """Identificador do modelo."""
        return f"google-{self.model_name}"

    def is_available(self) -> bool:
        """Verifica se ha credenciais configuradas para o Gemini."""
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    def generate_hypothesis_and_action(
        self,
        area_name: str,
        metrics_summary: str,
        context_events: List[Dict[str, Any]],
        shap_narrative: str,
        factor: str,
    ) -> Tuple[str, str]:
        """Invoca o Gemini para correlacionar metricas SHAP com contexto organizacional."""
        if not self.is_available():
            raise RuntimeError(
                f"Provedor '{self.name}' indisponivel: GEMINI_API_KEY ausente ou invalida."
            )

        prompt = (
            f"Voce e o Pulso, Digital Worker de Governanca de Riscos Psicossociais (NR-1).\n"
            f"Analise a area: {area_name}\n"
            f"Sintese de Metricas: {metrics_summary}\n"
            f"Explicabilidade SHAP do XGBoost: {shap_narrative}\n"
            f"Fator de Risco NR-1: {factor}\n"
            f"Eventos Organizacionais Recentes: {context_events}\n\n"
            f"Tarefas:\n"
            f"1. Redija uma hipotese de contexto clara conectando a anomalia aos eventos.\n"
            f"2. Sugira um plano de acao preventivo formal para o PGR com reavaliacao em 60 dias.\n"
        )

        try:
            genai = importlib.import_module("google.generativeai")
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            text = response.text.strip()

            parts = text.split("\n\n")
            hypothesis = str(parts[0]) if len(parts) > 0 else str(text)
            action = (
                str(parts[1])
                if len(parts) > 1
                else "Revisao de processo e inclusao no PGR em 60 dias."
            )
            return hypothesis, action
        except Exception as exc:
            raise RuntimeError(f"Erro na execucao da API Gemini: {str(exc)}") from exc

    def generate_chat_reply(
        self,
        query_text: str,
        context_data: Dict[str, Any],
    ) -> str:
        """Gera resposta em linguagem natural via Gemini."""
        if not self.is_available():
            raise RuntimeError(f"Provedor '{self.name}' sem chave configurada.")

        try:
            genai = importlib.import_module("google.generativeai")
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(
                f"Contexto NR-1: {context_data}\nPergunta do RH: {query_text}\n"
                f"Responda apenas sobre dados agregados de equipes sem identificar colaboradores."
            )
            return str(response.text.strip())
        except Exception as exc:
            raise RuntimeError(f"Falha na resposta do Gemini: {str(exc)}") from exc
