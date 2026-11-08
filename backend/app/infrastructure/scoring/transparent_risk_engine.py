"""Regras operacionais versionadas. Nao e ML, SHAP ou probabilidade clinica."""

from app.domain.entities.risk_factor import PsychosocialRiskFactor as Factor
from app.domain.entities.risk_factor import RiskLevel
from app.infrastructure.ml.xgboost_risk_engine import RiskPredictionResult


class TransparentRiskEngine:
    version = "rules-v1-demo"

    def predict(
        self,
        *,
        variacao_dias_atestado_pct: float,
        variacao_horas_extras_pct: float,
        pedidos_demissao: float,
        media_empresa_pedidos_demissao: float,
        queda_nota_clima: float,
        denuncias_compliance: int = 0,
    ) -> RiskPredictionResult:
        # Limiares da demonstracao, exigem revisao especializada antes de piloto.
        if denuncias_compliance >= 3:
            score, level, factor, rule = 95.0, RiskLevel.VERMELHO, Factor.ASSEDIO, "COMPLIANCE_3"
        elif variacao_dias_atestado_pct >= 30 and variacao_horas_extras_pct >= 40:
            score, level, factor, rule = (
                80.0,
                RiskLevel.VERMELHO,
                Factor.SOBRECARGA_METAS,
                "CARGA_30_40",
            )
        elif pedidos_demissao >= 4:
            score, level, factor, rule = (
                68.0,
                RiskLevel.AMARELO,
                Factor.LIDERANCA_CONFLITO,
                "SAIDAS_VOLUNTARIAS_4",
            )
        else:
            score, level, factor, rule = (
                12.0,
                RiskLevel.VERDE,
                Factor.ESTAVEL_SEM_FATOR,
                "SEM_LIMIAR_ATINGIDO",
            )
        return RiskPredictionResult(
            risk_score=score,
            risk_level=level,
            probable_factor=factor,
            shap_breakdown=[],
            audit_narrative=f"Regra {rule}; versao {self.version}. Indicador operacional, sem diagnostico ou inferencia causal.",
        )
