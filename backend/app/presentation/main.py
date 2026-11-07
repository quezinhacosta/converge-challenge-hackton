"""Fabrica e ponto de entrada da aplicacao FastAPI do vitAI (Pulso).

Exporta a aplicacao completa contendo os endpoints da Pessoa B (/fechamento, /areas/{id},
/casos/{id}/decisao, /chat/query) e os endpoints da API v1 para o frontend Angular.
"""

from app.main import app, create_app as create_application

__all__ = ["app", "create_application"]
