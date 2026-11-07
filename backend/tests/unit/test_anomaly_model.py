"""Validation tests for the ML anomaly model training pipeline."""

from pathlib import Path
import joblib
import pandas as pd
from scripts.train_anomaly_model import generate_synthetic_payroll_dataset, train_and_export_model


def test_synthetic_data_generation() -> None:
    """Verify synthetic dataset produces expected shape and columns."""
    df = generate_synthetic_payroll_dataset(normal_samples=50, anomaly_samples=5)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 55
    expected_cols = ["salario_base", "he_mes", "he_media_3m", "desvio_setor"]
    assert list(df.columns) == expected_cols


def test_model_training_and_serialization(tmp_path: Path) -> None:
    """Verify Isolation Forest model can be trained, saved, and reloaded."""
    temp_model_path = tmp_path / "test_model.pkl"
    train_and_export_model(output_path=temp_model_path)

    assert temp_model_path.exists()
    loaded_model = joblib.load(temp_model_path)
    assert hasattr(loaded_model, "predict")
