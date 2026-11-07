import React from 'react';

export interface MetricsCardProps {
  /** Metric card header label. */
  title: string;
  /** Primary metric value or amount. */
  value: string | number;
  /** Contextual comparison or trend description. */
  subtitle?: string;
  /** Visual indicator type (e.g. success, alert, danger, neutral). */
  variant?: 'neutral' | 'success' | 'warning' | 'danger';
}

/**
 * MetricsCard Component.
 *
 * Reusable summary metric card for DP dashboard KPIs (e.g., Blocked Fraud Value,
 * High-Risk Anomalies, INSS Referrals, Total Batch Headcount).
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
