import React from 'react';
import { AnomalyReport } from '@/types/payroll';

export interface AuditActionCenterProps {
  /** Lista de anomalias detectadas aguardando analise humana do DP. */
  pendingAnomalies: AnomalyReport[];
  /** Callback executado quando o analista aprova ou rejeita o lancamento retido. */
  onResolveAnomaly: (anomalyId: string, approved: boolean, note: string) => Promise<void>;
  /** Montante financeiro total retido preventivamente. */
  totalBlockedAmount: number;
}

/**
 * Componente AuditActionCenter.
 *
 * Implementa o painel de governanca Human-in-the-Loop para o Departamento Pessoal.
 * Permite a tomada de decisao em 1 clique (aprovar ou rejeitar), exibindo o PayTrust Score
 * e a fundamentacao trabalhista elaborada pela IA de compliance.
 */
export const AuditActionCenter: React.FC<AuditActionCenterProps> = ({
  pendingAnomalies,
  onResolveAnomaly,
  totalBlockedAmount,
}) => {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-xl font-semibold text-slate-900">Central de Governanca e Acoes do DP</h2>
      <p className="mt-1 text-sm text-slate-500">
        Revise os itens criticos da folha e execute decisoes de compliance em 1 clique.
      </p>
      {/* Stub de implementacao da interface visual */}
    </div>
  );
};
