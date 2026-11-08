"""Motor de Risco treinado carregando artefatos de modelo (Gradient Boosted + SHAP).

Implementa `BaseRiskEngine` e se integra diretamente com a arquitetura do vitAI.
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional

# Adiciona o diretorio do backend ao sys.path caso necessario para imports
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.domain.entities.risk_factor import PsychosocialRiskFactor, RiskLevel
from app.infrastructure.ml.xgboost_risk_engine import (
    BaseRiskEngine,
    RiskPredictionResult,
    ShapContribution,
    set_active_risk_engine,
)


class DecisionStumpRunner:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.feature_index: int = data["feature_index"]
        self.threshold: float = data["threshold"]
        self.left_value: float = data["left_value"]
        self.right_value: float = data["right_value"]

    def predict_one(self, x: List[float]) -> float:
        if x[self.feature_index] <= self.threshold:
            return self.left_value
        return self.right_value


class TrainedRiskEngine(BaseRiskEngine):
    """Motor preditivo que executa inferencia baseada no modelo treinado em `artifacts/model_weights.json`."""

    def __init__(self, weights_path: Optional[str] = None) -> None:
        if weights_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            weights_path = os.path.join(base_dir, "artifacts", "model_weights.json")

        self.weights_path = weights_path
        if not os.path.exists(weights_path):
            raise FileNotFoundError(
                f"Artefato de pesos nao encontrado em {weights_path}. Execute 'python3 train_model.py' primeiro."
            )

        with open(weights_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.learning_rate: float = data.get("learning_rate", 0.15)
        self.base_score: float = data.get("base_score", 45.0)
        self.feature_names: List[str] = data.get("feature_names", [])
        self.feature_labels: Dict[str, str] = data.get("feature_labels", {})
        self.trees: List[DecisionStumpRunner] = [
            DecisionStumpRunner(t) for t in data.get("trees", [])
        ]

    def predict(
        self,
        variacao_dias_atestado_pct: float,
        variacao_horas_extras_pct: float,
        pedidos_demissao: int,
        media_empresa_pedidos_demissao: float,
        queda_nota_clima: float,
        denuncias_compliance: int = 0,
    ) -> RiskPredictionResult:
        """Executa a inferencia do modelo treinado sobre as features observadas."""
        features = [
            float(variacao_dias_atestado_pct),
            float(variacao_horas_extras_pct),
            float(pedidos_demissao),
            float(media_empresa_pedidos_demissao),
            float(queda_nota_clima),
            float(denuncias_compliance),
        ]

        # Inferencia aditiva
        pred_score = self.base_score
        feature_contributions = {feat: 0.0 for feat in self.feature_names}

        for tree in self.trees:
            increment = self.learning_rate * tree.predict_one(features)
            pred_score += increment
            feat_name = self.feature_names[tree.feature_index]
            feature_contributions[feat_name] += increment

        # Caso critico de compliance / assedio sobrepoe com isolamento etico
        if denuncias_compliance >= 3:
            pred_score = max(pred_score, 82.0)
            probable_factor = PsychosocialRiskFactor.ASSEDIO
            risk_level = RiskLevel.VERMELHO
        else:
            pred_score = max(5.0, min(99.0, pred_score))
            if pred_score >= 70.0:
                risk_level = RiskLevel.VERMELHO
            elif pred_score >= 35.0:
                risk_level = RiskLevel.AMARELO
            else:
                risk_level = RiskLevel.VERDE

            # Classificacao de fator preponderante
            if queda_nota_clima >= 0.8 and pedidos_demissao >= (media_empresa_pedidos_demissao * 1.5):
                probable_factor = PsychosocialRiskFactor.LIDERANCA_CONFLITO
            elif variacao_horas_extras_pct >= 20.0 or variacao_dias_atestado_pct >= 30.0:
                probable_factor = PsychosocialRiskFactor.SOBRECARGA_METAS
            elif pred_score >= 40.0:
                probable_factor = PsychosocialRiskFactor.SOBRECARGA_METAS
            else:
                probable_factor = PsychosocialRiskFactor.ESTAVEL_SEM_FATOR

        # Calcula decomposicao percentual SHAP
        abs_sum = sum(abs(v) for v in feature_contributions.values()) or 1.0
        shap_items: List[ShapContribution] = []

        feature_display_values = {
            "variacao_dias_atestado_pct": f"{variacao_dias_atestado_pct:+.1f}% vs media anterior",
            "variacao_horas_extras_pct": f"{variacao_horas_extras_pct:+.1f}% no fechamento do mes",
            "pedidos_demissao": f"{pedidos_demissao} saidas voluntarias (media emp.: {media_empresa_pedidos_demissao})",
            "media_empresa_pedidos_demissao": f"Media corporativa: {media_empresa_pedidos_demissao}",
            "queda_nota_clima": f"Delta de queda: {queda_nota_clima:.1f} pontos na pesquisa",
            "denuncias_compliance": f"{denuncias_compliance} denuncias registradas",
        }

        for feat_name, raw_impact in feature_contributions.items():
            pct = round((abs(raw_impact) / abs_sum) * 100.0, 1)
            shap_items.append(
                ShapContribution(
                    feature_name=feat_name,
                    display_name=self.feature_labels.get(feat_name, feat_name),
                    contribution_pct=pct,
                    observed_value=feature_display_values.get(feat_name, str(raw_impact)),
                    direction="AGRAVANTE" if raw_impact >= 0 else "ATENUANTE",
                )
            )

        # Ajusta soma para 100.0%
        shap_items.sort(key=lambda s: s.contribution_pct, reverse=True)
        total_pct = sum(s.contribution_pct for s in shap_items)
        if shap_items and abs(total_pct - 100.0) > 0.01:
            diff = round(100.0 - total_pct, 1)
            shap_items[0].contribution_pct = round(shap_items[0].contribution_pct + diff, 1)

        narrative = (
            f"Modelo treinado calculou score de risco de {pred_score:.1f}/100 ({risk_level.value}). "
            f"Fator preponderante identificado: {probable_factor.value}."
        )

        return RiskPredictionResult(
            risk_score=round(pred_score, 1),
            risk_level=risk_level,
            probable_factor=probable_factor,
            shap_breakdown=shap_items,
            audit_narrative=narrative,
        )


def activate_trained_engine(weights_path: Optional[str] = None) -> TrainedRiskEngine:
    """Instancia o motor treinado e o define como o motor ativo na aplicacao vitAI."""
    engine = TrainedRiskEngine(weights_path)
    set_active_risk_engine(engine)
    print("TrainedRiskEngine ativado com sucesso no vitAI.")
    return engine
