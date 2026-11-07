"""Caso de uso para auditoria de lote de folha, calculo do score de ML e alerta de anomalias."""

from typing import List, Protocol
import pandas as pd

from app.application.dtos.payroll_dto import (
    PayrollBatchAuditRequestDTO,
    PayrollBatchAuditResponseDTO,
)
from app.domain.repositories.interfaces import AnomalyRepository, PayrollRepository


class AnomalyDetectorService(Protocol):
    """Protocolo definindo o contrato do servico de deteccao de anomalias por Machine Learning."""

    def predict_scores(self, features_df: pd.DataFrame) -> List[float]:
        """Calcula o PayTrust Score continuo (0 a 100) para cada item do lote."""
        ...


class ComplianceAgentService(Protocol):
    """Protocolo definindo o servico generativo de explicabilidade juridico-trabalhista."""

    def explain_anomaly(
        self, employee_id: str, score: float, metrics: dict
    ) -> str:
        """Gera uma explicacao em linguagem natural para um desvio de folha identificado."""
        ...


class AuditPayrollUseCase:
    """Coordena a auditoria do lote de folha combinando Camada 1 (ML) e Camada 2 (LLM).

    Fluxo de Execucao:
        1. Ingestao dos registros do lote de folha submetidos pelo DP ou ERP.
        2. Extracao do vetor de caracteristicas: [salario_base, he_mes, he_media_3m, desvio_setor].
        3. Execucao da inferencia pelo Isolation Forest gerando o PayTrust Score (0 a 100).
        4. Filtragem dos itens cujo score ultrapasse o limiar critico de risco (ex.: Score >= 80).
        5. Invocacao do Agente de Compliance para redigir a justificativa baseada na CLT.
        6. Persistencia dos apontamentos de anomalia para analise humana em 1 clique.
        7. Devolucao do relatorio consolidado para o dashboard do DP.
    """

    def __init__(
        self,
        anomaly_detector: AnomalyDetectorService,
        compliance_agent: ComplianceAgentService,
        payroll_repository: PayrollRepository,
        anomaly_repository: AnomalyRepository,
    ) -> None:
        """Inicializa o caso de uso com os adaptadores e repositorios necessarios.

        Argumentos:
            anomaly_detector: Servico responsavel pela inferencia do modelo Isolation Forest.
            compliance_agent: Servico de LLM que formula a explicacao legal do desvio.
            payroll_repository: Camada de persistencia para holerites e lotes.
            anomaly_repository: Camada de persistencia para os registros de anomalia.
        """
        self.anomaly_detector = anomaly_detector
        self.compliance_agent = compliance_agent
        self.payroll_repository = payroll_repository
        self.anomaly_repository = anomaly_repository

    def execute(self, request: PayrollBatchAuditRequestDTO) -> PayrollBatchAuditResponseDTO:
        """Executa a esteira de auditoria preditiva no lote de folha de pagamento.

        Argumentos:
            request: Payload contendo a colecao de registros de colaboradores a avaliar.

        Retorna:
            PayrollBatchAuditResponseDTO: Sumario da auditoria, valores retidos e anomalias.

        Lanca:
            ValueError: Se o lote estiver vazio ou contiver dados inconsistentes.
        """
        raise NotImplementedError("AuditPayrollUseCase.execute e um stub de interface estrutural.")
