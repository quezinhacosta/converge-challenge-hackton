import React from 'react';
import { Paystub } from '@/types/payroll';

export interface InteractivePaystubProps {
  /** The detailed paystub object for the selected period. */
  paystub: Paystub;
  /** Callback to request conversational AI clarification on any rubric code. */
  onRequestExplanation: (rubricCode: string) => void;
}

/**
 * InteractivePaystub Component.
 *
 * Provides a modern, transparent paystub visualization for employees. Every rubric
 * (e.g., INSS discounts, Súmula 159 substitution differential, overtime breakdown)
 * is interactive and can be explained in plain language by the AI compliance agent.
 */
export const InteractivePaystub: React.FC<InteractivePaystubProps> = ({
  paystub,
  onRequestExplanation,
}) => {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-xl font-semibold text-slate-900">Explainable Paystub</h2>
      {/* Component UI implementation stub */}
    </div>
  );
};
