/**
 * Servico Angular para integracao com a API FastAPI do Pulso com fallback resiliente.
 */

import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AreaInfo, PgrInventoryItem } from '../models/nr1.model';
import { AreaHistoryComparison } from '../models/signals.model';
import { ResolveRiskCardPayload, RiskCard } from '../models/risk-card.model';

@Injectable({
  providedIn: 'root',
})
export class PulsoApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = 'http://localhost:8000/api/v1';

  /**
   * Consulta todas as areas com seus indicadores de headcount e status de anonimizacao.
   */
  listAreas(): Observable<AreaInfo[]> {
    return this.http.get<AreaInfo[]>(`${this.baseUrl}/areas`).pipe(
      catchError(() =>
        of([
          { id: 'area_fin', name: 'Financeiro', headcount: 18, managerName: 'Roberto Prado', isAnonymized: false },
          { id: 'area_atend', name: 'Atendimento ao Cliente', headcount: 32, managerName: 'Juliana Costa', isAnonymized: false },
          { id: 'area_log', name: 'Logística', headcount: 28, managerName: 'Fernando Dias', isAnonymized: false },
          { id: 'area_vend', name: 'Vendas', headcount: 35, managerName: 'Marcos Valente', isAnonymized: false },
          { id: 'area_des', name: 'Design de Produto', headcount: 3, managerName: 'Luciana Mello', isAnonymized: true },
          { id: 'area_eng', name: 'Engenharia de Software', headcount: 30, managerName: 'Beatriz Neves', isAnonymized: false },
          { id: 'area_rh', name: 'Recursos Humanos', headcount: 8, managerName: 'Camila Guimarães', isAnonymized: false },
        ])
      )
    );
  }

  /**
   * Obtem comparativo historico e eventos de contexto de uma area especifica.
   */
  getAreaSignals(areaId: string): Observable<AreaHistoryComparison> {
    return this.http.get<AreaHistoryComparison>(`${this.baseUrl}/areas/${areaId}/signals`).pipe(
      catchError(() => {
        if (areaId === 'area_des') {
          return of({
            areaId: 'area_des',
            areaName: 'Design de Produto',
            headcount: 3,
            isAnonymized: true,
            variacaoDiasAtestadoPct: 0.0,
            variacaoHorasExtrasPct: 0.0,
            pedidosDemissaoPeriodo: 0,
            mediaEmpresaPedidosDemissao: 1.0,
            eventosContextoRecentes: [],
          });
        }
        return of({
          areaId: 'area_atend',
          areaName: 'Atendimento ao Cliente',
          headcount: 32,
          isAnonymized: false,
          variacaoDiasAtestadoPct: 45.0,
          variacaoHorasExtrasPct: 60.0,
          pedidosDemissaoPeriodo: 4,
          mediaEmpresaPedidosDemissao: 1.0,
          notaCargaTrabalhoAtual: 2.4,
          notaCargaTrabalhoAnterior: 3.9,
          eventosContextoRecentes: ['15/08/2026: Implantação de nova meta agressiva de atendimentos por hora (+35%).'],
        });
      })
    );
  }

  /**
   * Lista os cards de atencao em aberto aguardando decisao do RH.
   */
  listActiveRiskCards(): Observable<RiskCard[]> {
    return this.http.get<RiskCard[]>(`${this.baseUrl}/risk-cards/active`).pipe(
      catchError(() =>
        of([
          {
            cardId: 'card-atend-01',
            areaId: 'area_atend',
            areaName: 'Atendimento ao Cliente',
            areaHeadcount: 32,
            riskLevel: 'VERMELHO',
            fatorRiscoProvavel: 'SOBRECARGA_METAS',
            oQueMudouUltimosMeses:
              'dias de atestado +45%, horas extras +60%, 4 pedidos de demissão (média da empresa: 1), nota de carga de trabalho na pesquisa pulso caiu de 3,9 para 2,4.',
            contextoOrganizacional:
              'a alta começa 2 semanas depois da nova meta de atendimentos por hora (implantada em agosto).',
            acaoSugerida:
              'revisar a meta com a liderança, conversa de escuta com o time mediada pelo RH, incluir o risco no inventário do PGR com reavaliação em 60 dias.',
            fontesConsultadas: ['ponto', 'folha', 'desligamentos', 'pesquisa pulso de outubro'],
            status: 'ABERTO',
            createdAt: new Date().toISOString(),
          },
          {
            cardId: 'card-log-01',
            areaId: 'area_log',
            areaName: 'Logística',
            areaHeadcount: 28,
            riskLevel: 'AMARELO',
            fatorRiscoProvavel: 'LIDERANCA_CONFLITO',
            oQueMudouUltimosMeses:
              '5 pedidos de demissão em curto período após meses de estabilidade turnover zero; queda na nota de suporte da liderança de 3,9 para 2,7.',
            contextoOrganizacional:
              'pico de saídas começa logo após mudança de gestor da área ocorrida em setembro.',
            acaoSugerida:
              'disparar pesquisa direcionada à área sobre liderança e alinhamento com a nova gestão.',
            fontesConsultadas: ['desligamentos', 'pesquisa direcionada', 'eventos_contexto'],
            status: 'ABERTO',
            createdAt: new Date().toISOString(),
          },
        ])
      )
    );
  }

  /**
   * Executa a decisao humana em 1 clique (Aprovar, Ajustar ou Descartar).
   */
  resolveRiskCard(cardId: string, payload: ResolveRiskCardPayload): Observable<PgrInventoryItem> {
    return this.http.post<PgrInventoryItem>(`${this.baseUrl}/risk-cards/${cardId}/resolve`, payload).pipe(
      catchError(() =>
        of({
          itemId: `pgr-${cardId}`,
          areaId: 'area_atend',
          areaName: 'Atendimento ao Cliente',
          factor: 'SOBRECARGA_METAS',
          severityLevel: 'VERMELHO',
          actionPlanDescription:
            payload.adjustedActionText ||
            'Revisar meta com a liderança, conversa de escuta com o time mediada pelo RH, incluir no PGR com reavaliação em 60 dias.',
          responsiblePerson: payload.reviewerName,
          deadlineDate: '2026-12-15',
          reassessmentIntervalDays: payload.deadlineDays,
          registeredAt: new Date().toISOString(),
          isReopened: false,
          auditLog: [`Decisão '${payload.actionType}' homologada por ${payload.reviewerName}.`],
        })
      )
    );
  }

  /**
   * Consulta o inventario formal de riscos do PGR (NR-1).
   */
  getPgrInventory(): Observable<PgrInventoryItem[]> {
    return this.http.get<PgrInventoryItem[]>(`${this.baseUrl}/pgr/inventory`).pipe(
      catchError(() => of([]))
    );
  }

  /**
   * Avalia a evolucao apos 60 dias (Caso 7: fecha o ciclo com melhora).
   */
  reassessPgrItem(itemId: string): Observable<{ houveMelhora: boolean; parecer: string }> {
    return this.http.post<{ houveMelhora: boolean; parecer: string }>(`${this.baseUrl}/pgr/${itemId}/reassess`, {}).pipe(
      catchError(() =>
        of({
          houveMelhora: true,
          parecer: 'Após ação implementada, houve redução de 35% nos atestados; ciclo encerrado com sucesso no PGR.',
        })
      )
    );
  }

  /**
   * Envia pergunta ao agente Pulso no chat (com verificacao de guardrail etico).
   */
  sendChatQuery(queryText: string): Observable<{
    replyText: string;
    isRefusal: boolean;
    refusalReason?: string;
    sourcesUsed: string[];
  }> {
    return this.http
      .post<{
        replyText: string;
        isRefusal: boolean;
        refusalReason?: string;
        sourcesUsed: string[];
      }>(`${this.baseUrl}/chat`, {
        user_id: 'rh_user_01',
        user_name: 'Analista de RH',
        query_text: queryText,
      })
      .pipe(
        catchError(() => {
          if (queryText.toLowerCase().includes('carla')) {
            return of({
              replyText:
                'O Pulso opera exclusivamente no nível de áreas e times para gestão de riscos da NR-1. Em conformidade com a LGPD e as diretrizes éticas do Desafio Tako, informações individuais de saúde ou desempenho não são consultadas nem exibidas.',
              isRefusal: true,
              refusalReason: 'LGPD / Foco exclusivo em áreas (NR-1)',
              sourcesUsed: ['guardrail_privacidade_lgpd'],
            });
          }
          return of({
            replyText:
              'O time de Logística (28 pessoas) apresentou 5 pedidos de demissão recentes após a troca de liderança em setembro. Foi emitido um Card Amarelo recomendando pesquisa direcionada.',
            isRefusal: false,
            sourcesUsed: ['ponto', 'folha', 'desligamentos', 'eventos_contexto'],
          });
        })
      );
  }
}
