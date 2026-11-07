"""Training script for the PayTrust Isolation Forest anomaly detection model.

Generates synthetic baseline payroll distributions and anomalous spikes, trains
an Isolation Forest model, and exports the serialized model artifact (.pkl)
for integration with the FastAPI backend inference pipeline.
"""

from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

DEFAULT_OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent
    / "app"
    / "infrastructure"
    / "ml"
    / "paytrust_anomaly.pkl"
)


def generate_synthetic_payroll_dataset(
    normal_samples: int = 800, anomaly_samples: int = 50, random_state: int = 42
) -> pd.DataFrame:
    """Generate synthetic payroll features simulating normal employees and fraudulent spikes.

    Feature Definitions:
        - salario_base: Contracted monthly base salary in BRL.
        - he_mes: Overtime hours logged in the current audit period.
        - he_media_3m: Historic 3-month rolling average of overtime hours.
        - desvio_setor: Deviation of overtime hours relative to departmental peers.

    Args:
        normal_samples: Count of regular payroll observations to synthesize.
        anomaly_samples: Count of severe overtime/deviation anomalies to inject.
        random_state: Seed for reproducible data generation.

    Returns:
        pd.DataFrame: Consolidated dataset containing normal and anomalous observations.
    """
    rng = np.random.default_rng(random_state)

    # 1. Normal baseline records
    normais = rng.normal(
        loc=[5000, 10, 10, 0], scale=[1000, 3, 3, 10], size=(normal_samples, 4)
    )

    # 2. Fraudulent or aberrant records (abnormal overtime spikes, extreme sector deviations)
    anomalias = rng.uniform(
        low=[3000, 45, 5, 200], high=[8000, 80, 10, 500], size=(anomaly_samples, 4)
    )

    dataset_matrix = np.vstack([normais, anomalias])
    return pd.DataFrame(
        dataset_matrix,
        columns=["salario_base", "he_mes", "he_media_3m", "desvio_setor"],
    )


def train_and_export_model(
    output_path: Path = DEFAULT_OUTPUT_PATH, contamination_rate: float = 0.06
) -> Path:
    """Train the Isolation Forest model on synthetic payroll data and export artifact.

    Args:
        output_path: Target filesystem location for the .pkl artifact.
        contamination_rate: Expected proportion of outliers in the training distribution.

    Returns:
        Path: Destination path of the saved artifact.
    """
    dataset = generate_synthetic_payroll_dataset()

    model = IsolationForest(contamination=contamination_rate, random_state=42)
    model.fit(dataset)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_path)
    print(f"PayTrust model successfully compiled and serialized to: {output_path}")

    return output_path


if __name__ == "__main__":
    train_and_export_model()
