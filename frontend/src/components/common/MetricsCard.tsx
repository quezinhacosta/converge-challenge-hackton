import React from 'react';

export interface MetricsCardProps {
  /** Titulo ou rotulo do card de metrica. */
  title: string;
  /** Valor principal em destaque (monetario ou quantidade). */
  value: string | number;
  /** Subtitulo contextual ou comparativo com meses anteriores. */
  subtitle?: string;
  /** Variante visual de status (neutro, sucesso, alerta, perigo). */
  variant?: 'neutral' | 'success' | 'warning' | 'danger';
}

/**
 * Componente MetricsCard.
 *
 * Card visual reutilizavel para exibicao de KPIs do DP (ex.: Montante Retido de Fraude,
 * Total de Anomalias de Alto Risco, Encaminhamentos ao INSS, Vidas Auditadas no Lote).
 */
export const MetricsCard: React.FC<MetricsCardProps> = ({
  title,
  value,
  subtitle,
  variant = 'neutral',
}) => {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="text-sm font-medium text-slate-500">{title}</div>
      <div className="mt-2 text-2xl font-bold text-slate-900">{value}</div>
      {subtitle && <div className="mt-1 text-xs text-slate-400">{subtitle}</div>}
    </div>
  );
};
