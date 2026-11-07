import React from 'react';
import { Paystub } from '@/types/payroll';

export interface InteractivePaystubProps {
  /** Objeto de holerite detalhado da competencia selecionada. */
  paystub: Paystub;
  /** Callback para solicitar explicacao interativa da IA sobre qualquer rubrica. */
  onRequestExplanation: (rubricCode: string) => void;
}

/**
 * Componente InteractivePaystub.
 *
 * Exibe o holerite interativo para o colaborador. Cada rubrica (ex.: descontos de INSS,
 * diferenca da Sumula 159, detalhamento de horas extras) e clicavel e pode ser explicada
 * em linguagem humana e transparente pelo agente de compliance.
 */
export const InteractivePaystub: React.FC<InteractivePaystubProps> = ({
  paystub,
  onRequestExplanation,
}) => {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-xl font-semibold text-slate-900">Holerite Interativo Explicavel</h2>
      {/* Stub de implementacao da interface visual */}
    </div>
  );
};
