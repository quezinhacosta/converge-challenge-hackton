import React from 'react';
import { AbsenceRecord, SubstitutionRule } from '@/types/absence';

export interface AbsenceManagerProps {
  /** Collection of active employee leaves and medical certificates. */
  absences: AbsenceRecord[];
  /** Calculated substitution cases governed by Súmula 159 TST. */
  substitutions: SubstitutionRule[];
  /** Handler to generate and dispatch INSS scheduling instructions. */
  onDispatchInssNotice: (absenceId: string) => Promise<void>;
}

/**
 * AbsenceManager Component.
 *
 * Manages medical leave routing: validates the 15-day employer responsibility threshold,
 * forwards long-term cases to INSS, detects vacation clashes, and computes non-occasional
 * substitution wage adjustments under Brazilian labor jurisprudence.
 */
export const AbsenceManager: React.FC<AbsenceManagerProps> = ({
  absences,
  substitutions,
  onDispatchInssNotice,
}) => {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-xl font-semibold text-slate-900">Absence & Substitution Manager</h2>
      <p className="mt-1 text-sm text-slate-500">
        Automated 15-day CLT / INSS splits and Súmula 159 TST wage adjustments.
      </p>
      {/* Component UI implementation stub */}
    </div>
  );
};
