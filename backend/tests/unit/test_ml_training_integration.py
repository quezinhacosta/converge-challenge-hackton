"""Teste de integracao do motor treinado na pasta ml_training com o backend vitAI."""

import os
import sys
import pytest

from app.domain.entities.risk_factor import RiskLevel
from app.infrastructure.ml import get_active_risk_engine, set_active_risk_engine

# Adiciona ml_training ao path
ml_training_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml_training"))
if ml_training_dir not in sys.path:
    sys.path.insert(0, ml_training_dir)

from trained_engine import TrainedRiskEngine, activate_trained_engine


def test_trained_engine_plug_and_predict() -> None:
    original_engine = get_active_risk_engine()
    try:
        # Ativa o motor treinado
        engine = activate_trained_engine()
        assert get_active_risk_engine() is engine

        # Predicao de equipe estavel
        res_estavel = engine.predict(
            variacao_dias_atestado_pct=1.0,
            variacao_horas_extras_pct=0.5,
            pedidos_demissao=0,
            media_empresa_pedidos_demissao=1.0,
            queda_nota_clima=0.0,
            denuncias_compliance=0,
        )
        assert res_estavel.risk_level == RiskLevel.VERDE
        assert res_estavel.risk_score < 30.0
        assert len(res_estavel.shap_breakdown) > 0

        # Predicao de sobrecarga
        res_sobrecarga = engine.predict(
            variacao_dias_atestado_pct=45.0,
            variacao_horas_extras_pct=40.0,
            pedidos_demissao=2,
            media_empresa_pedidos_demissao=1.0,
            queda_nota_clima=0.8,
            denuncias_compliance=0,
        )
        assert res_sobrecarga.risk_level == RiskLevel.VERMELHO
        assert res_sobrecarga.risk_score >= 70.0
    finally:
        set_active_risk_engine(original_engine)
