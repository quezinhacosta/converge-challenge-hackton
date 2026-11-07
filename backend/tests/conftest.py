"""Configuracao global dos testes: nunca chamar o LLM real na suite unitaria."""

import os

# Precisa rodar antes de importar app.presentation.deps (que cria o container no import).
os.environ["PULSO_LLM_ENABLED"] = "false"
os.environ.pop("GEMINI_API_KEY", None)
