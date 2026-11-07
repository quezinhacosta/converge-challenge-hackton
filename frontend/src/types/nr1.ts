/**
 * Tipos TypeScript para a gestao de riscos psicossociais da NR-1 e inventario do PGR.
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
  headcount: int;
  managerName: string;
  isAnonymized: boolean; // true se headcount < 5
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
}
