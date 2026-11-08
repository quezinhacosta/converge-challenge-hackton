"""Modulo de Machine Learning e Explicabilidade SHAP."""

from app.infrastructure.ml.xgboost_risk_engine import (
    BaseRiskEngine,
    RiskEngineProtocol,
    RiskPredictionResult,
    ShapContribution,
    XGBoostRiskEngine,
    get_active_risk_engine,
    set_active_risk_engine,
)

__all__ = [
    "BaseRiskEngine",
    "RiskEngineProtocol",
    "XGBoostRiskEngine",
    "RiskPredictionResult",
    "ShapContribution",
    "get_active_risk_engine",
    "set_active_risk_engine",
]
