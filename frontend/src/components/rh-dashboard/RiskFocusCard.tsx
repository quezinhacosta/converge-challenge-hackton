import React from 'react';
import { RiskCard, ResolveRiskCardPayload } from '@/types/riskCard';

export interface RiskFocusCardProps {
  /** Dados do card de atencao emitido pelo Pulso. */
  card: RiskCard;
  /** Callback para resolucao em 1 clique pelo analista de RH. */
  onResolve: (cardId: string, payload: ResolveRiskCardPayload) => Promise<void>;
}

/**
 * Componente RiskFocusCard (Ponto Focal de Atencao do RH).
 *
 * Apresenta o card de atencao priorizado com evidencias dos ultimos 3 meses,
 * correlacao temporal com eventos de contexto, hipotese de fator de risco da NR-1,
 * proposta de acao e botoes de deliberacao humana:
 * [ Aprovar e registrar no PGR ] [ Ajustar acao ] [ Descartar com justificativa ]
 */
export const RiskFocusCard: React.FC<RiskFocusCardProps> = ({ card, onResolve }) => {
  return (
    <div className="rounded-xl border border-rose-200 bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
        <div>
          <span className="inline-flex items-center rounded-full bg-rose-100 px-2.5 py-0.5 text-xs font-semibold text-rose-800">
            ATENCAO {card.riskLevel}
          </span>
          <h3 className="mt-1 text-lg font-bold text-slate-900">
            Area: {card.areaName} ({card.areaHeadcount} pessoas)
          </h3>
        </div>
        <span className="text-xs text-slate-400">Status: {card.status}</span>
      </div>

      <div className="mt-4 space-y-3 text-sm text-slate-700">
        <div>
          <strong className="text-slate-900">O que mudou nos ultimos 3 meses:</strong>{' '}
          {card.oQueMudouUltimosMeses}
        </div>
        <div>
          <strong className="text-slate-900">Contexto:</strong> {card.contextoOrganizacional}
        </div>
        <div>
          <strong className="text-slate-900">Fator de risco provavel:</strong>{' '}
          <span className="font-semibold text-indigo-700">{card.fatorRiscoProvavel}</span>
        </div>
        <div className="rounded-lg bg-amber-50 p-3 text-amber-900">
          <strong>Acao sugerida:</strong> {card.acaoSugerida}
        </div>
        <div className="text-xs text-slate-500">
          <strong>Fontes consultadas:</strong> {card.fontesConsultadas.join(', ')}
        </div>
      </div>

      {/* Botoes de Decisao Humana (Human-in-the-Loop) */}
      <div className="mt-6 flex flex-wrap gap-2 border-t border-slate-100 pt-4">
        <button
          type="button"
          className="rounded-md bg-emerald-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-emerald-700"
          onClick={() =>
            onResolve(card.cardId, {
              actionType: 'APROVAR_PGR',
              reviewerName: 'Analista de RH',
              deadlineDays: 60,
            })
          }
        >
          Aprovar e registrar no PGR
        </button>
        <button
          type="button"
          className="rounded-md bg-slate-100 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-200"
          onClick={() =>
            onResolve(card.cardId, {
              actionType: 'AJUSTAR_ACAO',
              reviewerName: 'Analista de RH',
              deadlineDays: 60,
            })
          }
        >
          Ajustar acao
        </button>
        <button
          type="button"
          className="rounded-md bg-rose-50 px-3 py-1.5 text-xs font-medium text-rose-700 hover:bg-rose-100"
          onClick={() =>
            onResolve(card.cardId, {
              actionType: 'DESCARTAR',
              reviewerName: 'Analista de RH',
              deadlineDays: 0,
              justificationNotes: 'Sem evidencias suficientes apos verificacao com lideranca.',
            })
          }
        >
          Descartar com justificativa
        </button>
      </div>
    </div>
  );
};
