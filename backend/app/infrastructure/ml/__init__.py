"""Adaptadores de Machine Learning para deteccao preditiva de anomalias na folha."""

from app.infrastructure.ml.anomaly_detector import SklearnAnomalyDetector

__all__ = ["SklearnAnomalyDetector"]
