/**
 * Interface do cliente de integracao com a API FastAPI do Pulso.
 */

import { AreaInfo, PgrInventoryItem } from '../types/nr1';
import { AreaHistoryComparison } from '../types/signals';
import { ResolveRiskCardPayload, RiskCard } from '../types/riskCard';

export interface PulsoApiClient {
  /**
   * Consulta todas as areas com seus indicadores de headcount e anonimizacao.
   */
  listAreas(): Promise<AreaInfo[]>;

  /**
   * Obtem comparativo historico e eventos de contexto de uma area especifica.
   */
  getAreaSignals(areaId: string): Promise<AreaHistoryComparison>;

  /**
   * Lista os cards de atencao em aberto aguardando decisao do RH.
   */
  listActiveRiskCards(): Promise<RiskCard[]>;

  /**
   * Executa a decisao humana em 1 clique (Aprovar, Ajustar ou Descartar).
   */
  resolveRiskCard(cardId: string, payload: ResolveRiskCardPayload): Promise<PgrInventoryItem>;

  /**
   * Consulta o inventario formal de riscos do PGR (NR-1).
   */
  getPgrInventory(): Promise<PgrInventoryItem[]>;

  /**
   * Envia pergunta ao agente Pulso no chat (com verificacao de guardrail etico).
   */
  sendChatQuery(queryText: string): Promise<{
    replyText: string;
    isRefusal: boolean;
    refusalReason?: string;
    sourcesUsed: string[];
  }>;
}
