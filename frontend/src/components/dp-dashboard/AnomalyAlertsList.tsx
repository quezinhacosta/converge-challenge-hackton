import React from 'react';
import { AnomalyReport } from '@/types/payroll';

export interface AnomalyAlertsListProps {
  /** Array of anomalies flagged by the Layer 1 ML model. */
  alerts: AnomalyReport[];
  /** Callback invoked when an alert card is selected for in-depth inspection. */
  onSelectAlert: (alert: AnomalyReport) => void;
}

/**
 * AnomalyAlertsList Component.
 *
 * Renders priority alert cards sorted by PayTrust Score (0 to 100), highlighting
 * severe overtime deviations, unverified benefits, and ghost worker anomalies.
 */
export const AnomalyAlertsList: React.FC<AnomalyAlertsListProps> = ({
  alerts,
  onSelectAlert,
}) => {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-medium text-slate-800">Priority Anomaly Alerts</h3>
      {/* Component UI implementation stub */}
    </div>
  );
};
