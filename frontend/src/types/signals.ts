/**
 * Tipos TypeScript para sinais operacionais agregados e comparativos historicos.
 */

export interface AreaMetrics {
  areaId: string;
  areaName: string;
  competencePeriod: string;
  certificateDaysCount: number;
  certificateCasesCount: number;
  unexcusedAbsencesCount: number;
  shiftCoveragesCount: number;
  resignationRequestsCount: number;
  turnoverRate: number;
  overtimeHoursAvg: number;
  harassmentComplaintsCount: number;
  pulseSurveyWorkloadScore?: number;
}

export interface AreaHistoryComparison {
  areaId: string;
  areaName: string;
  headcount: number;
  isAnonymized: boolean;
  variacaoDiasAtestadoPct: number;
  variacaoHorasExtrasPct: number;
  pedidosDemissaoPeriodo: number;
  mediaEmpresaPedidosDemissao: number;
  notaCargaTrabalhoAtual?: number;
  notaCargaTrabalhoAnterior?: number;
  eventosContextoRecentes: string[];
}
