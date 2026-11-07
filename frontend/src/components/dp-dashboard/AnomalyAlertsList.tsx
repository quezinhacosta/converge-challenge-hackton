import React from 'react';
import { AnomalyReport } from '@/types/payroll';

export interface AnomalyAlertsListProps {
  /** Colecao de anomalias detectadas pelo motor de ML da Camada 1. */
  alerts: AnomalyReport[];
  /** Callback acionado ao selecionar um card de anomalia para auditoria detalhada. */
  onSelectAlert: (alert: AnomalyReport) => void;
}

/**
 * Componente AnomalyAlertsList.
 *
 * Renderiza os cards de apontamento priorizados pelo PayTrust Score (0 a 100),
 * destacando saltos de horas extras, adicionais suspeitos e funcionarios fantasmas.
 */
export const AnomalyAlertsList: React.FC<AnomalyAlertsListProps> = ({
  alerts,
  onSelectAlert,
}) => {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-medium text-slate-800">Alertas Prioritarios de Anomalia</h3>
      {/* Stub de implementacao da interface visual */}
    </div>
  );
};
