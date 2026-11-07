/**
 * API client interfaces and stubs for communication with the PayTrust FastAPI backend.
 */

import { BatchAuditSummary, AnomalyReport } from '../types/payroll';
import { AbsenceRecord, SubstitutionRule } from '../types/absence';

export interface PayTrustApiClient {
  /**
   * Upload and trigger predictive ML audit for a payroll batch.
   */
  auditBatch(file: File): Promise<BatchAuditSummary>;

  /**
   * Retrieve pending anomalies awaiting 1-click human DP analyst resolution.
   */
  getPendingAnomalies(): Promise<AnomalyReport[]>;

  /**
   * Resolve an anomaly (Human-in-the-Loop 1-click approve or reject).
   */
  resolveAnomaly(anomalyId: string, approved: boolean, note: string): Promise<void>;

  /**
   * Submit and parse an employee medical certificate via OCR Vision.
   */
  uploadMedicalCertificate(employeeId: string, file: File): Promise<AbsenceRecord>;

  /**
   * Calculate temporary substitution wage differential according to Súmula 159 TST.
   */
  calculateSubstitutionDifferential(params: {
    substituteId: string;
    replacedId: string;
    startDate: string;
    endDate: string;
  }): Promise<SubstitutionRule>;
}
