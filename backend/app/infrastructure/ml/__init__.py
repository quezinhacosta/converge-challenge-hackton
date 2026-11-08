"""Modulo de Machine Learning e Explicabilidade SHAP."""

from app.infrastructure.ml.xgboost_risk_engine import (
    RiskPredictionResult,
    ShapContribution,
    XGBoostRiskEngine,
    get_active_risk_engine,
    set_active_risk_engine,
)

__all__ = [
    "XGBoostRiskEngine",
    "RiskPredictionResult",
    "ShapContribution",
    "get_active_risk_engine",
    "set_active_risk_engine",
]
