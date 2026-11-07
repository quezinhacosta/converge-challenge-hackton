/**
 * Tipos TypeScript para os Cards de Ponto Focal do RH.
 */

import { PsychosocialRiskFactor, RiskLevel } from './nr1';

export type CardStatus = 'ABERTO' | 'APROVADO_PGR' | 'AJUSTADO' | 'DESCARTADO';

export interface RiskCard {
  cardId: string;
  areaId: string;
  areaName: string;
  areaHeadcount: number;
  riskLevel: RiskLevel;
  fatorRiscoProvavel: PsychosocialRiskFactor;
  oQueMudouUltimosMeses: string;
  contextoOrganizacional: string;
  acaoSugerida: string;
  fontesConsultadas: string[];
  status: CardStatus;
  createdAt: string;
}

export interface ResolveRiskCardPayload {
  actionType: 'APROVAR_PGR' | 'AJUSTAR_ACAO' | 'DESCARTAR';
  reviewerName: string;
  adjustedActionText?: string;
  responsiblePerson?: string;
  deadlineDays: number;
  justificationNotes?: string;
}
