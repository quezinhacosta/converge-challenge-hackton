"""Script de treino e compilacao do modelo Isolation Forest do PayTrust.

Gera dados sinteticos simulando distribuicoes normais de folha e desvios fraudulentos,
treina o modelo Isolation Forest e exporta o artefato serializado (.pkl)
para ser consumido na inferencia da API FastAPI.
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
    """Gera caracteristicas sinteticas simulando colaboradores padrao e fraudes em horas extras.

    Definicao das Features:
        - salario_base: Salario base mensal contratual em Reais.
        - he_mes: Horas extras totais registradas na competencia corrente.
        - he_media_3m: Media movel de horas extras dos 3 meses anteriores.
        - desvio_setor: Desvio das horas extras do colaborador em relacao aos pares do setor.

    Argumentos:
        normal_samples: Quantidade de observacoes regulares a simular.
        anomaly_samples: Quantidade de distorcoes atipicas de horas extras a injetar.
        random_state: Semente pseudo-aleatoria para reprodutibilidade.

    Retorna:
        pd.DataFrame: Conjunto de dados unificado contendo registros normais e anomalias.
    """
    rng = np.random.default_rng(random_state)

    # 1. Registros normais da rotina da empresa
    normais = rng.normal(loc=[5000, 10, 10, 0], scale=[1000, 3, 3, 10], size=(normal_samples, 4))

    # 2. Desvios atipicos e fraudes (picos desproporcionais de H.E. e desvio setorial extremo)
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
    """Treina o modelo Isolation Forest no conjunto sintetico e exporta o artefato compilado.

    Argumentos:
        output_path: Caminho de destino para salvar o arquivo .pkl serializado.
        contamination_rate: Proporcao esperada de outliers na distribuicao de treino.

    Retorna:
        Path: Caminho do arquivo onde o modelo foi salvo.
    """
    dataset = generate_synthetic_payroll_dataset()

    model = IsolationForest(contamination=contamination_rate, random_state=42)
    model.fit(dataset)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_path)
    print(f"Modelo PayTrust compilado e serializado com sucesso em: {output_path}")

    return output_path


if __name__ == "__main__":
    train_and_export_model()
