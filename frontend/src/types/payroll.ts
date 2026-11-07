/**
 * TypeScript type definitions for payroll entities, audit batches, and ML anomaly findings.
 */

export type RiskSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type AnomalyCategory =
  | 'OVERTIME_SPIKE'
  | 'GHOST_EMPLOYEE'
  | 'DUPLICATE_PAYMENT'
  | 'SUBSTITUTION_MISMATCH'
  | 'VACATION_OVERLAP'
  | 'SUSPICIOUS_ADDITIONAL';

export interface PaystubItem {
  code: string;
  description: string;
  referenceUnits: number;
  amount: number;
  isDiscount: boolean;
}

export interface Paystub {
  id: string;
  employeeId: string;
  employeeName: string;
  competencePeriod: string;
  baseSalary: number;
  overtimeHoursCurrentMonth: number;
  overtimeHours3mAverage: number;
  sectorOvertimeDeviation: number;
  substitutionSalaryDifferential: number;
  grossTotal: number;
  netTotal: number;
  items: PaystubItem[];
}

export interface AnomalyReport {
  anomalyId: string;
  employeeId: string;
  employeeName: string;
  category: AnomalyCategory;
  severity: RiskSeverity;
  paytrustScore: number; // 0 to 100
  explanation: string;
  actionRecommended: string;
  isResolved: boolean;
}

export interface BatchAuditSummary {
  batchId: string;
  totalRecordsAnalyzed: number;
  totalAnomaliesDetected: number;
  totalBlockedAmountBrl: number;
  anomalies: AnomalyReport[];
}
