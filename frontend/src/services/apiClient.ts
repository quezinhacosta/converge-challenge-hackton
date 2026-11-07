/**
 * Interface do cliente de integracao com a API FastAPI do PayTrust.
 */

import { BatchAuditSummary, AnomalyReport } from '../types/payroll';
import { AbsenceRecord, SubstitutionRule } from '../types/absence';

export interface PayTrustApiClient {
  /**
   * Envia lote de folha para auditoria preditiva via modelo Isolation Forest.
   */
  auditBatch(file: File): Promise<BatchAuditSummary>;

  /**
   * Recupera anomalias pendentes aguardando revisao humana em 1 clique pelo DP.
   */
  getPendingAnomalies(): Promise<AnomalyReport[]>;

  /**
   * Resolve uma anomalia (Human-in-the-Loop: aprovar liberacao ou rejeitar pagamento).
   */
  resolveAnomaly(anomalyId: string, approved: boolean, note: string): Promise<void>;

  /**
   * Envia atestado medico para extracao e validacao automatica via OCR Vision.
   */
  uploadMedicalCertificate(employeeId: string, file: File): Promise<AbsenceRecord>;

  /**
   * Calcula a diferenca salarial proporcional por substituicao conforme a Sumula 159 do TST.
   */
  calculateSubstitutionDifferential(params: {
    substituteId: string;
    replacedId: string;
    startDate: string;
    endDate: string;
  }): Promise<SubstitutionRule>;
}
