import React from 'react';
import { AreaHistoryComparison } from '@/types/signals';

export interface AreaSignalsViewProps {
  /** Dados agregados e historico comparativo da area. */
  areaComparison: AreaHistoryComparison;
}

/**
 * Componente AreaSignalsView.
 *
 * Apresenta a visualizacao comparativa dos sinais operacionais da area (atestados,
 * horas extras, desligamentos e notas de clima).
 *
 * Se a area possuir menos de 5 pessoas (isAnonymized === true), oculta integralmente os
 * dados e emite alerta amigavel de protecao por exclusao conforme os guardrails da NR-1.
 */
export const AreaSignalsView: React.FC<AreaSignalsViewProps> = ({ areaComparison }) => {
  if (areaComparison.isAnonymized) {
    return (
      <div className="rounded-xl border border-amber-200 bg-amber-50 p-6 text-amber-900">
        <h3 className="font-bold">
          Dados Ocultados para Protecao de Privacidade (Quorom &lt; 5 pessoas)
        </h3>
        <p className="mt-2 text-sm">
          A area <strong>{areaComparison.areaName}</strong> possui apenas {areaComparison.headcount}{' '}
          colaboradores. Para impedir a identificacao de pessoas por exclusao, os indicadores
          agregados nao sao exibidos nesta visualizacao.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="text-lg font-bold text-slate-900">
        Painel de Sinais: {areaComparison.areaName} ({areaComparison.headcount} pessoas)
      </h3>
      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
        <div className="rounded-lg bg-slate-50 p-3">
          <div className="text-xs text-slate-500">Variacao de Dias de Atestado</div>
          <div className="mt-1 text-xl font-bold text-slate-800">
            {areaComparison.variacaoDiasAtestadoPct > 0 ? '+' : ''}
            {areaComparison.variacaoDiasAtestadoPct}%
          </div>
        </div>
        <div className="rounded-lg bg-slate-50 p-3">
          <div className="text-xs text-slate-500">Variacao de Horas Extras</div>
          <div className="mt-1 text-xl font-bold text-slate-800">
            {areaComparison.variacaoHorasExtrasPct > 0 ? '+' : ''}
            {areaComparison.variacaoHorasExtrasPct}%
          </div>
        </div>
      </div>
    </div>
  );
};
