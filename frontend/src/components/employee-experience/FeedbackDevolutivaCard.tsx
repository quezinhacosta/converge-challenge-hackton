import React from 'react';

export interface FeedbackDevolutivaCardProps {
  /** Nome do setor. */
  areaName: string;
  /** Resumo do feedback recebido da equipe. */
  summaryOfListening: string;
  /** Plano de acao formalizado pela lideranca e RH. */
  actionPlanExplanation: string;
}

/**
 * Componente FeedbackDevolutivaCard.
 *
 * Exibe o comunicado de devolutiva transparente ("Voce falou, a empresa fez").
 * Fecha o ciclo de confianca com o colaborador, demonstrando que a escuta ativa
 * gerou acoes concretas e mudancas reais no ambiente de trabalho.
 */
export const FeedbackDevolutivaCard: React.FC<FeedbackDevolutivaCardProps> = ({
  areaName,
  summaryOfListening,
  actionPlanExplanation,
}) => {
  return (
    <div className="rounded-xl border border-emerald-200 bg-emerald-50/60 p-6 shadow-sm">
      <div className="flex items-center gap-2 text-emerald-800">
        <span className="rounded-full bg-emerald-200 px-2.5 py-0.5 text-xs font-bold uppercase tracking-wider">
          Voce falou, a empresa fez
        </span>
        <span className="text-xs text-emerald-700">Equipe: {areaName}</span>
      </div>

      <h3 className="mt-2 text-lg font-bold text-slate-900">
        Comunicado de Melhoria e Cuidado com a Equipe
      </h3>

      <div className="mt-3 space-y-2 text-sm text-slate-700">
        <div>
          <strong className="text-slate-900">O que ouvimos de voces:</strong> {summaryOfListening}
        </div>
        <div className="rounded-lg bg-white p-3 border border-emerald-100 text-slate-800">
          <strong className="text-emerald-900">O que vai mudar a partir de agora:</strong>{' '}
          {actionPlanExplanation}
        </div>
      </div>
    </div>
  );
};
