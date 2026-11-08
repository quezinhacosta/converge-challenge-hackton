"""Testes para plugar motores customizados de Machine Learning no vitAI."""

from app.domain.entities.risk_factor import PsychosocialRiskFactor, RiskLevel
from app.infrastructure.ml.xgboost_risk_engine import (
    BaseRiskEngine,
    RiskPredictionResult,
    ShapContribution,
    XGBoostRiskEngine,
    get_active_risk_engine,
    set_active_risk_engine,
)
from app.main import executar_fechamento_mensal


class CustomMockRiskEngine(BaseRiskEngine):
    """Exemplo de motor customizado implementado pelo usuario."""

    def predict(
        self,
        variacao_dias_atestado_pct: float,
        variacao_horas_extras_pct: float,
        pedidos_demissao: int,
        media_empresa_pedidos_demissao: float,
        queda_nota_clima: float,
        denuncias_compliance: int = 0,
    ) -> RiskPredictionResult:
        return RiskPredictionResult(
            risk_score=99.9,
            risk_level=RiskLevel.VERMELHO,
            probable_factor=PsychosocialRiskFactor.SOBRECARGA_METAS,
            shap_breakdown=[
                ShapContribution(
                    feature_name="delta_atestados",
                    display_name="Custom Motor - Atestados",
                    contribution_pct=70.0,
                    observed_value=f"{variacao_dias_atestado_pct}%",
                ),
                ShapContribution(
                    feature_name="queda_nota_clima",
                    display_name="Custom Motor - Clima",
                    contribution_pct=30.0,
                    observed_value=f"{queda_nota_clima}",
                ),
            ],
            audit_narrative="Predicao gerada pelo motor customizado do usuario.",
        )


def test_custom_engine_registration_and_fechamento() -> None:
    """Verifica que ao registrar um novo motor, o fechamento utiliza os resultados desse motor."""
    original_engine = get_active_risk_engine()
    try:
        custom_engine = CustomMockRiskEngine()
        set_active_risk_engine(custom_engine)

        assert get_active_risk_engine() is custom_engine

        # Executa o fechamento
        resultado = executar_fechamento_mensal()
        assert resultado.total_areas >= 7

        # Verifica que os casos elegiveis receberam o score e a narrativa do custom engine
        casos_elegiveis = [c for c in resultado.casos_gerados if c.status != "BLOCKED_PRIVACY"]
        assert len(casos_elegiveis) > 0

        primeiro_caso = casos_elegiveis[0]
        assert primeiro_caso.score_risco == 99.9
        assert primeiro_caso.nivel_risco == "VERMELHO"
        assert "motor customizado" in (primeiro_caso.narrativa_explicabilidade or "")
    finally:
        # Restaura o motor padrao
        set_active_risk_engine(original_engine)
