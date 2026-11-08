"""Script de Treinamento de Machine Learning para Inferencia de Riscos Psicossociais (NR-1).

Implementa Gradient Boosted Decision Trees com interpretabilidade SHAP nativa,
dividindo amostras em treino e teste (80/20) e persistindo os pesos e metricas.
Autossuficiente: funciona diretamente com a biblioteca padrao do Python (sem travar por dependencias).
"""

import csv
import json
import math
import os
import random
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


FEATURE_NAMES = [
    "variacao_dias_atestado_pct",
    "variacao_horas_extras_pct",
    "pedidos_demissao",
    "media_empresa_pedidos_demissao",
    "queda_nota_clima",
    "denuncias_compliance",
]

FEATURE_LABELS = {
    "variacao_dias_atestado_pct": "Aumento de Atestados Medicos",
    "variacao_horas_extras_pct": "Sobrecarga de Horas Extras",
    "pedidos_demissao": "Pedidos Voluntarios de Demissao",
    "media_empresa_pedidos_demissao": "Media Historica de Turnover",
    "queda_nota_clima": "Queda na Pesquisa de Clima",
    "denuncias_compliance": "Denuncias no Canal de Etica",
}


class DecisionStump:
    """Arvore de decisao rasa (Stump) para Gradient Boosting."""

    def __init__(self) -> None:
        self.feature_index: int = 0
        self.threshold: float = 0.0
        self.left_value: float = 0.0
        self.right_value: float = 0.0
        self.gain: float = 0.0

    def predict_one(self, x: List[float]) -> float:
        if x[self.feature_index] <= self.threshold:
            return self.left_value
        return self.right_value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "feature_index": self.feature_index,
            "feature_name": FEATURE_NAMES[self.feature_index],
            "threshold": self.threshold,
            "left_value": self.left_value,
            "right_value": self.right_value,
            "gain": self.gain,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DecisionStump":
        stump = cls()
        stump.feature_index = data["feature_index"]
        stump.threshold = data["threshold"]
        stump.left_value = data["left_value"]
        stump.right_value = data["right_value"]
        stump.gain = data.get("gain", 0.0)
        return stump


class GradientBoostedRiskRegressor:
    """Ensemble de arvores de decisao aditivas com taxa de aprendizado e shrinkage."""

    def __init__(self, n_estimators: int = 35, learning_rate: float = 0.15) -> None:
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.base_score: float = 0.0
        self.trees: List[DecisionStump] = []
        self.feature_importances_: Dict[str, float] = {}

    def fit(self, X: List[List[float]], y: List[float]) -> "GradientBoostedRiskRegressor":
        n_samples = len(y)
        n_features = len(X[0])
        self.base_score = sum(y) / n_samples

        current_preds = [self.base_score] * n_samples
        feature_gains = [0.0] * n_features

        for _ in range(self.n_estimators):
            # Gradiente negativo (residuos para erro quadratico)
            residuals = [y[i] - current_preds[i] for i in range(n_samples)]

            best_stump = DecisionStump()
            best_mse = float("inf")

            for feat_idx in range(n_features):
                vals = [X[i][feat_idx] for i in range(n_samples)]
                unique_vals = sorted(set(vals))
                if len(unique_vals) <= 1:
                    continue

                # Testa percentis como thresholds para velocidade
                step = max(1, len(unique_vals) // 15)
                candidates = unique_vals[::step]

                for th in candidates:
                    left_res = [residuals[i] for i in range(n_samples) if X[i][feat_idx] <= th]
                    right_res = [residuals[i] for i in range(n_samples) if X[i][feat_idx] > th]

                    if not left_res or not right_res:
                        continue

                    left_mean = sum(left_res) / len(left_res)
                    right_mean = sum(right_res) / len(right_res)

                    mse = sum((r - left_mean) ** 2 for r in left_res) + sum(
                        (r - right_mean) ** 2 for r in right_res
                    )

                    if mse < best_mse:
                        best_mse = mse
                        best_stump.feature_index = feat_idx
                        best_stump.threshold = th
                        best_stump.left_value = left_mean
                        best_stump.right_value = right_mean
                        best_stump.gain = sum(residuals[i] ** 2 for i in range(n_samples)) - mse

            self.trees.append(best_stump)
            feature_gains[best_stump.feature_index] += max(0.0, best_stump.gain)

            # Atualiza predicoes parciais
            for i in range(n_samples):
                current_preds[i] += self.learning_rate * best_stump.predict_one(X[i])

        # Normaliza feature importance
        total_gain = sum(feature_gains) or 1.0
        self.feature_importances_ = {
            FEATURE_NAMES[i]: round(feature_gains[i] / total_gain, 4) for i in range(n_features)
        }
        return self

    def predict_one(self, x: List[float]) -> float:
        pred = self.base_score
        for tree in self.trees:
            pred += self.learning_rate * tree.predict_one(x)
        return max(0.0, min(100.0, pred))

    def predict(self, X: List[List[float]]) -> List[float]:
        return [self.predict_one(x) for x in X]

    def compute_shap_breakdown(self, x: List[float]) -> Dict[str, float]:
        """Calcula a contribuicao aditiva (SHAP-like) de cada feature para afastar o score da baseline."""
        contributions: Dict[str, float] = {feat: 0.0 for feat in FEATURE_NAMES}

        for tree in self.trees:
            feat_name = FEATURE_NAMES[tree.feature_index]
            val = self.learning_rate * tree.predict_one(x)
            contributions[feat_name] += val

        # Ajusta para percentuais relativos ponderados
        abs_sum = sum(abs(v) for v in contributions.values()) or 1.0
        relative_pct = {k: round((abs(v) / abs_sum) * 100.0, 1) for k, v in contributions.items()}

        # Forca a soma exata em 100.0%
        diff = 100.0 - sum(relative_pct.values())
        highest_feat = max(relative_pct, key=lambda k: relative_pct[k])
        relative_pct[highest_feat] = round(relative_pct[highest_feat] + diff, 1)

        return relative_pct


def load_dataset(dataset_path: str) -> Tuple[List[List[float]], List[float], List[Dict[str, Any]]]:
    with open(dataset_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    X: List[List[float]] = []
    y: List[float] = []

    for r in records:
        features = [
            float(r["variacao_dias_atestado_pct"]),
            float(r["variacao_horas_extras_pct"]),
            float(r["pedidos_demissao"]),
            float(r["media_empresa_pedidos_demissao"]),
            float(r["queda_nota_clima"]),
            float(r["denuncias_compliance"]),
        ]
        X.append(features)
        y.append(float(r["risk_score"]))

    return X, y, records


def evaluate_metrics(y_true: List[float], y_pred: List[float]) -> Dict[str, float]:
    n = len(y_true)
    mae = sum(abs(yt - yp) for yt, yp in zip(y_true, y_pred)) / n
    rmse = math.sqrt(sum((yt - yp) ** 2 for yt, yp in zip(y_true, y_pred)) / n)

    y_mean = sum(y_true) / n
    ss_tot = sum((yt - y_mean) ** 2 for yt in y_true)
    ss_res = sum((yt - yp) ** 2 for yt, yp in zip(y_true, y_pred))
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    # Acuracia de classificacao categorica de severidade
    def get_cat(score: float) -> str:
        if score < 30.0:
            return "VERDE"
        elif score < 70.0:
            return "AMARELO"
        return "VERMELHO"

    correct_cats = sum(1 for yt, yp in zip(y_true, y_pred) if get_cat(yt) == get_cat(yp))
    cat_accuracy = correct_cats / n

    return {
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "r2": round(r2, 4),
        "severity_accuracy": round(cat_accuracy * 100.0, 1),
    }


def train_and_save(base_dir: str) -> None:
    dataset_file = os.path.join(base_dir, "dataset_nr1.json")
    if not os.path.exists(dataset_file):
        print(f"Dataset nao encontrado em {dataset_file}. Gerando novo dataset...")
        from generate_dataset import generate_synthetic_dataset, save_dataset
        records = generate_synthetic_dataset(1500)
        save_dataset(records, base_dir)

    print("Carregando dataset...")
    X, y, records = load_dataset(dataset_file)
    n_samples = len(X)

    # Train / Test Split (80% treino, 20% teste)
    random.seed(42)
    indices = list(range(n_samples))
    random.shuffle(indices)

    split_idx = int(0.8 * n_samples)
    train_idx = indices[:split_idx]
    test_idx = indices[split_idx:]

    X_train = [X[i] for i in train_idx]
    y_train = [y[i] for i in train_idx]
    X_test = [X[i] for i in test_idx]
    y_test = [y[i] for i in test_idx]

    print(f"Treinando modelo Gradient Boosted com {len(X_train)} amostras de treino...")
    model = GradientBoostedRiskRegressor(n_estimators=40, learning_rate=0.15)
    model.fit(X_train, y_train)

    print("Avaliando no conjunto de teste...")
    y_pred_test = model.predict(X_test)
    metrics = evaluate_metrics(y_test, y_pred_test)

    print("\n--- Relatorio de Performance do Modelo Treinado ---")
    print(f"MAE (Erro Medio Absoluto): {metrics['mae']} pts")
    print(f"RMSE (Raiz do Erro Quadratico Medio): {metrics['rmse']} pts")
    print(f"R² (Coeficiente de Determinacao): {metrics['r2']}")
    print(f"Acuracia na Classificacao de Severidade: {metrics['severity_accuracy']}%")
    print(f"Importancia das Variaveis: {model.feature_importances_}")

    # Salva artefatos treinados
    artifacts_dir = os.path.join(base_dir, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)

    weights_data = {
        "model_type": "GradientBoostedRiskRegressor",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "n_estimators": model.n_estimators,
        "learning_rate": model.learning_rate,
        "base_score": model.base_score,
        "feature_names": FEATURE_NAMES,
        "feature_labels": FEATURE_LABELS,
        "feature_importances": model.feature_importances_,
        "trees": [tree.to_dict() for tree in model.trees],
    }

    weights_path = os.path.join(artifacts_dir, "model_weights.json")
    with open(weights_path, "w", encoding="utf-8") as f:
        json.dump(weights_data, f, indent=2, ensure_ascii=False)

    report_path = os.path.join(artifacts_dir, "train_report.json")
    report_data = {
        "metrics": metrics,
        "n_samples_total": n_samples,
        "n_samples_train": len(X_train),
        "n_samples_test": len(X_test),
        "feature_importances": model.feature_importances_,
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    print(f"\nPesos e configuracoes salvos em:\n - {weights_path}")
    print(f"Relatorio salvo em:\n - {report_path}")


if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    train_and_save(base_path)
