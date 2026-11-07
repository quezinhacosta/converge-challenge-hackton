import React from 'react';
import { PgrInventoryItem } from '@/types/nr1';

export interface PgrInventoryTableProps {
  /** Colecao de registros de riscos e planos de acao do PGR. */
  items: PgrInventoryItem[];
  /** Callback para executar a reavaliacao apos 60 dias. */
  onReassess: (itemId: string) => Promise<void>;
}

/**
 * Componente PgrInventoryTable.
 *
 * Exibe o inventario oficial de riscos psicossociais e planos de acao da NR-1 (GRO/PGR),
 * contendo historico auditavel pronto para apresentacao em caso de fiscalizacao do MTE.
 */
export const PgrInventoryTable: React.FC<PgrInventoryTableProps> = ({ items, onReassess }) => {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-200 pb-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">
            Inventario de Riscos e Plano de Acao (PGR / NR-1)
          </h2>
          <p className="mt-1 text-sm text-slate-500">
            Documentacao formal e auditavel exigida pela Portaria MTE nº 1.419/2024.
          </p>
        </div>
      </div>

      <div className="mt-4 overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
          <thead className="bg-slate-50 text-xs font-semibold text-slate-700">
            <tr>
              <th className="px-4 py-3">Area</th>
              <th className="px-4 py-3">Fator Psicossocial</th>
              <th className="px-4 py-3">Nivel</th>
              <th className="px-4 py-3">Plano de Acao</th>
              <th className="px-4 py-3">Responsavel</th>
              <th className="px-4 py-3">Prazo</th>
              <th className="px-4 py-3">Acompanhamento</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {items.map((item) => (
              <tr key={item.itemId} className="hover:bg-slate-50">
                <td className="px-4 py-3 font-medium text-slate-900">{item.areaName}</td>
                <td className="px-4 py-3 text-slate-600">{item.factor}</td>
                <td className="px-4 py-3">
                  <span className="rounded px-2 py-0.5 text-xs font-semibold bg-rose-100 text-rose-800">
                    {item.severityLevel}
                  </span>
                </td>
                <td className="px-4 py-3 text-slate-700">{item.actionPlanDescription}</td>
                <td className="px-4 py-3 text-slate-600">{item.responsiblePerson}</td>
                <td className="px-4 py-3 text-slate-600">{item.deadlineDate}</td>
                <td className="px-4 py-3">
                  <button
                    type="button"
                    onClick={() => onReassess(item.itemId)}
                    className="text-xs text-indigo-600 hover:text-indigo-800 font-medium"
                  >
                    Reavaliar (60 dias)
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
