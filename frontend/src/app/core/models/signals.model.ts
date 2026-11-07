/**
 * Modelos para metricas operacionais agregadas e comparativos historicos.
 */

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
