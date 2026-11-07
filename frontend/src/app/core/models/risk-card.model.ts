/**
 * Modelos para os Cards de Ponto Focal de Atencao do RH com explicabilidade SHAP e resiliencia.
 */

import { PsychosocialRiskFactor, RiskLevel } from './nr1.model';

export type CardStatus = 'ABERTO' | 'APROVADO_PGR' | 'AJUSTADO' | 'DESCARTADO';

export interface ShapContribution {
  feature_name: string;
  display_name: string;
  contribution_pct: number;
  observed_value: string;
  direction: 'AGRAVANTE' | 'ATENUANTE';
}

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
  riskScore?: number;
  shapBreakdown?: ShapContribution[];
  aiProviderUsed?: string;
  aiFallbackTriggered?: boolean;
}

export interface ResolveRiskCardPayload {
  actionType: 'APROVAR_PGR' | 'AJUSTAR_ACAO' | 'DESCARTAR';
  reviewerName: string;
  adjustedActionText?: string;
  responsiblePerson?: string;
  deadlineDays: number;
  justificationNotes?: string;
}
