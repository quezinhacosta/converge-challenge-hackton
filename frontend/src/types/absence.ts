/**
 * TypeScript type definitions for medical certificate OCR and absence statutory splits.
 */

export type AbsenceType = 'MEDICAL' | 'MATERNITY' | 'BEREAVEMENT' | 'VACATION' | 'UNEXCUSED';

export type AbsenceStatus =
  | 'PENDING_VALIDATION'
  | 'APPROVED_COMPANY'
  | 'FORWARDED_TO_INSS'
  | 'REJECTED';

export interface AbsenceRecord {
  id: string;
  employeeId: string;
  employeeName: string;
  absenceType: AbsenceType;
  startDate: string;
  endDate: string;
  durationDays: number;
  companyPaidDays: number;
  inssPaidDays: number;
  status: AbsenceStatus;
  requiresInssScheduling: boolean;
  hasVacationConflict: boolean;
  icdCode?: string;
  documentUrl?: string;
}

export interface SubstitutionRule {
  substituteEmployeeId: string;
  replacedEmployeeId: string;
  startDate: string;
  endDate: string;
  durationDays: number;
  substituteBaseSalary: number;
  replacedBaseSalary: number;
  proportionalDifferentialAmount: number;
  isEligibleSumula159: boolean;
  legalRationale: string;
}
