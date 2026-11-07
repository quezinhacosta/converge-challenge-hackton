/**
 * Modelos TypeScript do Angular para fatores de risco da NR-1 e itens do PGR.
 */

export type RiskLevel = 'VERDE' | 'AMARELO' | 'VERMELHO';

export type PsychosocialRiskFactor =
  | 'SOBRECARGA_METAS'
  | 'JORNADAS_LONGAS'
  | 'LIDERANCA_CONFLITO'
  | 'ASSEDIO'
  | 'FALTA_CLAREZA_PAPEL'
  | 'FALTA_AUTONOMIA'
  | 'INSEGURANCA_TRABALHO'
  | 'ESTAVEL_SEM_FATOR';

export interface AreaInfo {
  id: string;
  name: string;
  headcount: number;
  managerName: string;
  isAnonymized: boolean;
}

export interface PgrInventoryItem {
  itemId: string;
  areaId: string;
  areaName: string;
  factor: PsychosocialRiskFactor;
  severityLevel: RiskLevel;
  actionPlanDescription: string;
  responsiblePerson: string;
  deadlineDate: string;
  reassessmentIntervalDays: number;
  registeredAt: string;
  isReopened: boolean;
  closureDate?: string;
  closureNotes?: string;
  auditLog: string[];
}
