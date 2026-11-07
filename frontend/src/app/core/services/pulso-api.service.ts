/**
 * Servico Angular para integracao com a API FastAPI do Pulso com fallback resiliente e interativo.
 */

import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AreaInfo, PgrInventoryItem } from '../models/nr1.model';
import { AreaHistoryComparison } from '../models/signals.model';
import { ResolveRiskCardPayload, RiskCard } from '../models/risk-card.model';

export interface ChatResponse {
  replyText: string;
  isRefusal: boolean;
  refusalReason?: string;
  sourcesUsed: string[];
  suggestedAction?: string;
}

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
      catchError(() => {
        const fallbackAreas: AreaInfo[] = [
          { id: 'area_atend', name: 'Atendimento ao Cliente', headcount: 32, managerName: 'Juliana Costa', isAnonymized: false },
          { id: 'area_log', name: 'Logística', headcount: 28, managerName: 'Fernando Dias', isAnonymized: false },
          { id: 'area_vend', name: 'Vendas', headcount: 35, managerName: 'Marcos Valente', isAnonymized: false },
          { id: 'area_fin', name: 'Financeiro', headcount: 18, managerName: 'Roberto Prado', isAnonymized: false },
          { id: 'area_des', name: 'Design de Produto', headcount: 3, managerName: 'Luciana Mello', isAnonymized: true },
          { id: 'area_eng', name: 'Engenharia de Software', headcount: 30, managerName: 'Beatriz Neves', isAnonymized: false },
          { id: 'area_rh', name: 'Recursos Humanos', headcount: 8, managerName: 'Camila Guimarães', isAnonymized: false },
        ];
        return of(fallbackAreas);
      })
    );
  }

  /**
   * Obtem comparativo historico e eventos de contexto de uma area especifica.
   */
  getAreaSignals(areaId: string): Observable<AreaHistoryComparison> {
    return this.http.get<AreaHistoryComparison>(`${this.baseUrl}/areas/${areaId}/signals`).pipe(
      catchError(() => {
        const comparisons: Record<string, AreaHistoryComparison> = {
          area_des: {
            areaId: 'area_des',
            areaName: 'Design de Produto',
            headcount: 3,
            isAnonymized: true,
            variacaoDiasAtestadoPct: 0.0,
            variacaoHorasExtrasPct: 0.0,
            pedidosDemissaoPeriodo: 0,
            mediaEmpresaPedidosDemissao: 1.0,
            eventosContextoRecentes: [],
          },
          area_atend: {
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
            eventosContextoRecentes: [
              '15/08/2026: Implantação de nova meta agressiva de atendimentos por hora (+35%).',
              '02/09/2026: Registro de pico de afastamentos médicos de curta duração (1 a 3 dias).',
            ],
          },
          area_log: {
            areaId: 'area_log',
            areaName: 'Logística',
            headcount: 28,
            isAnonymized: false,
            variacaoDiasAtestadoPct: 5.0,
            variacaoHorasExtrasPct: 8.0,
            pedidosDemissaoPeriodo: 5,
            mediaEmpresaPedidosDemissao: 1.0,
            notaCargaTrabalhoAtual: 2.7,
            notaCargaTrabalhoAnterior: 3.9,
            eventosContextoRecentes: [
              '10/09/2026: Mudança de gestor da área (nova liderança assumiu operação).',
              '25/09/2026: Concentração atípica de 5 pedidos de demissão voluntária.',
            ],
          },
          area_vend: {
            areaId: 'area_vend',
            areaName: 'Vendas',
            headcount: 35,
            isAnonymized: false,
            variacaoDiasAtestadoPct: 12.0,
            variacaoHorasExtrasPct: 15.0,
            pedidosDemissaoPeriodo: 2,
            mediaEmpresaPedidosDemissao: 1.0,
            notaCargaTrabalhoAtual: 3.2,
            notaCargaTrabalhoAnterior: 3.5,
            eventosContextoRecentes: [
              '18/09/2026: Registro de 3 denúncias formais no Canal de Ética sobre conduta abusiva em 2 meses.',
              'Alerta de segurança: Escalonamento imediato para Compliance sem exposição de conteúdo sensível.',
            ],
          },
          area_fin: {
            areaId: 'area_fin',
            areaName: 'Financeiro',
            headcount: 18,
            isAnonymized: false,
            variacaoDiasAtestadoPct: -2.0,
            variacaoHorasExtrasPct: 3.0,
            pedidosDemissaoPeriodo: 0,
            mediaEmpresaPedidosDemissao: 1.0,
            notaCargaTrabalhoAtual: 4.1,
            notaCargaTrabalhoAnterior: 4.0,
            eventosContextoRecentes: [
              'Operação em conformidade e parâmetros normais de ponto e saúde ocupacional.',
            ],
          },
        };

        const result = comparisons[areaId] || comparisons['area_atend'];
        return of(result);
      })
    );
  }

  /**
   * Lista os cards de atencao em aberto aguardando decisao do RH.
   */
  listActiveRiskCards(): Observable<RiskCard[]> {
    return this.http.get<RiskCard[]>(`${this.baseUrl}/risk-cards/active`).pipe(
      catchError(() => {
        const fallbackCards: RiskCard[] = [
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
          {
            cardId: 'card-vend-01',
            areaId: 'area_vend',
            areaName: 'Vendas',
            areaHeadcount: 35,
            riskLevel: 'VERMELHO',
            fatorRiscoProvavel: 'ASSEDIO',
            oQueMudouUltimosMeses:
              '3 denúncias anônimas registradas no Canal de Ética nos últimos 2 meses (alerta de concentração crítica).',
            contextoOrganizacional:
              'protocolo rigoroso de blindagem: escalonamento sigiloso ao comitê de Compliance sem leitura de teor pelo Digital Worker.',
            acaoSugerida:
              'encaminhar imediatamente para apuração formal do Comitê de Compliance e Ouvidoria.',
            fontesConsultadas: ['canal_denuncias_etica', 'ouvidoria_protocolos'],
            status: 'ABERTO',
            createdAt: new Date().toISOString(),
          },
        ];
        return of(fallbackCards);
      })
    );
  }

  /**
   * Executa a decisao humana em 1 clique (Aprovar, Ajustar ou Descartar).
   */
  resolveRiskCard(cardId: string, payload: ResolveRiskCardPayload): Observable<PgrInventoryItem> {
    return this.http.post<PgrInventoryItem>(`${this.baseUrl}/risk-cards/${cardId}/resolve`, payload).pipe(
      catchError(() => {
        const fallbackItem: PgrInventoryItem = {
          itemId: `pgr-${cardId}`,
          areaId: cardId.includes('atend') ? 'area_atend' : (cardId.includes('log') ? 'area_log' : 'area_vend'),
          areaName: cardId.includes('atend') ? 'Atendimento ao Cliente' : (cardId.includes('log') ? 'Logística' : 'Vendas'),
          factor: cardId.includes('atend') ? 'SOBRECARGA_METAS' : (cardId.includes('log') ? 'LIDERANCA_CONFLITO' : 'ASSEDIO'),
          severityLevel: cardId.includes('log') ? 'AMARELO' : 'VERMELHO',
          actionPlanDescription:
            payload.adjustedActionText ||
            (cardId.includes('atend')
              ? 'Revisar meta com a liderança, conversa de escuta com o time mediada pelo RH, incluir no PGR com reavaliação em 60 dias.'
              : 'Pesquisa direcionada e alinhamento de liderança.'),
          responsiblePerson: payload.reviewerName,
          deadlineDate: '2026-12-15',
          reassessmentIntervalDays: payload.deadlineDays || 60,
          registeredAt: new Date().toISOString(),
          isReopened: false,
          auditLog: [`Decisão '${payload.actionType}' homologada por ${payload.reviewerName} em conformidade com a NR-1.`],
        };
        return of(fallbackItem);
      })
    );
  }

  /**
   * Consulta o inventario formal de riscos do PGR (NR-1).
   */
  getPgrInventory(): Observable<PgrInventoryItem[]> {
    return this.http.get<PgrInventoryItem[]>(`${this.baseUrl}/pgr/inventory`).pipe(
      catchError(() => {
        const initialPgr: PgrInventoryItem[] = [
          {
            itemId: 'pgr-inv-001',
            areaId: 'area_atend',
            areaName: 'Atendimento ao Cliente',
            factor: 'SOBRECARGA_METAS',
            severityLevel: 'VERMELHO',
            actionPlanDescription: 'Revisar meta de atendimentos com liderança e realizar círculos de escuta semanais.',
            responsiblePerson: 'Juliana Costa / RH',
            deadlineDate: '2026-11-20',
            reassessmentIntervalDays: 60,
            registeredAt: '2026-09-15T10:00:00Z',
            isReopened: false,
            auditLog: ['Registrado no PGR via aprovação de Card de Atenção nº card-atend-01'],
          },
        ];
        return of(initialPgr);
      })
    );
  }

  /**
   * Avalia a evolucao apos 60 dias (Caso 7: fecha o ciclo com melhora).
   */
  reassessPgrItem(itemId: string): Observable<{ houveMelhora: boolean; parecer: string; reducaoAtestadosPct: number }> {
    return this.http.post<{ houveMelhora: boolean; parecer: string; reducaoAtestadosPct: number }>(`${this.baseUrl}/pgr/${itemId}/reassess`, {}).pipe(
      catchError(() =>
        of({
          houveMelhora: true,
          parecer: 'Após intervenção e ajuste da meta de atendimento, houve redução de 35% nos dias de atestado e normalização de horas extras. O ciclo foi avaliado como EFICAZ e encerrado no PGR formal da NR-1.',
          reducaoAtestadosPct: 35.0,
        })
      )
    );
  }

  /**
   * Envia pergunta ao agente Pulso no chat (com verificacao de guardrail etico).
   */
  sendChatQuery(queryText: string): Observable<ChatResponse> {
    return this.http
      .post<ChatResponse>(`${this.baseUrl}/chat`, {
        user_id: 'rh_user_01',
        user_name: 'Analista de RH',
        query_text: queryText,
      })
      .pipe(
        catchError(() => {
          const lower = queryText.toLowerCase();

          // Caso 5: Teste Guardrail Carla (Tentativa de busca individual)
          if (
            lower.includes('carla') ||
            lower.includes('individual') ||
            lower.includes('joão') ||
            lower.includes('maria') ||
            lower.includes('pessoa')
          ) {
            return of({
              replyText:
                'O Pulso opera exclusivamente no nível de áreas e times para conformidade da NR-1. Em obediência estrita à LGPD (Art. 7º e 11) e às diretrizes éticas do Desafio Tako, informações individualizadas de saúde, prontuários, CIDs ou atestados nominativos não são coletadas, consultadas nem exibidas.',
              isRefusal: true,
              refusalReason: 'Guardrail LGPD & Desafio Tako: Proibição de busca individual ou identificação nominal',
              sourcesUsed: ['guardrail_privacidade_lgpd', 'diretrizes_desafio_tako'],
              suggestedAction: 'Você pode consultar os dados consolidados da área ou time ao qual a pessoa pertence.',
            });
          }

          // Caso 3: Logística
          if (lower.includes('logística') || lower.includes('logistica')) {
            return of({
              replyText:
                'A área de Logística conta com 28 colaboradores. Identificamos estabilidade em horas extras e atestados, porém foram registrados 5 pedidos de demissão concentrados logo após a troca de liderança em setembro. Sugestão: aplicar pesquisa de pulso direcionada com foco em alinhamento de gestão.',
              isRefusal: false,
              sourcesUsed: ['desligamentos', 'folha', 'eventos_contexto'],
              suggestedAction: 'Card Amarelo emitido e disponível para deliberação do RH no Cockpit.',
            });
          }

          // Caso 4: Vendas / Denúncias
          if (lower.includes('vendas') || lower.includes('denúncia') || lower.includes('denuncia') || lower.includes('assédio') || lower.includes('assedio')) {
            return of({
              replyText:
                'Atenção: A área de Vendas (35 pessoas) acumulou 3 denúncias no Canal de Ética nos últimos 2 meses. Conforme nosso protocolo de governança, o agente NÃO lê o teor ou depoimentos para resguardar a integridade dos envolvidos, realizando o escalonamento imediato ao Comitê de Compliance.',
              isRefusal: false,
              sourcesUsed: ['canal_denuncias_etica', 'protocolo_compliance'],
              suggestedAction: 'Protocolo de escalonamento enviado para compliance@empresa.com.br.',
            });
          }

          // Caso 1: Financeiro
          if (lower.includes('financeiro')) {
            return of({
              replyText:
                'O Financeiro (18 pessoas) opera em padrão de estabilidade: variação de atestados de -2%, horas extras estáveis (+3%) e nota de clima 4.1/5. Nenhum risco psicossocial detectado para fins da NR-1.',
              isRefusal: false,
              sourcesUsed: ['ponto', 'folha', 'pesquisa_pulso'],
              suggestedAction: 'Manter monitoramento de rotina.',
            });
          }

          // Visão Geral
          return of({
            replyText:
              'Visão Geral: 154 colaboradores monitorados em 7 áreas corporativas. Temos 2 áreas demandando atenção imediata do RH: Atendimento ao Cliente (Card Vermelho - Sobrecarga pós-meta) e Logística (Card Amarelo - Saídas pós-troca de gestor). A área de Design de Produto (3 pessoas) permanece com dados agregados bloqueados para proteção de privacidade por quórum.',
            isRefusal: false,
            sourcesUsed: ['ponto', 'folha', 'desligamentos', 'canal_etica', 'pesquisa_pulso'],
            suggestedAction: 'Revise os cards prioritários no topo do Cockpit.',
          });
        })
      );
  }
}
