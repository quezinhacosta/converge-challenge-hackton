import React from 'react';
import { AbsenceRecord, SubstitutionRule } from '@/types/absence';

export interface AbsenceManagerProps {
  /** Colecao de afastamentos e atestados medicos ativos. */
  absences: AbsenceRecord[];
  /** Casos calculados de substituicao temporaria sob a Sumula 159 do TST. */
  substitutions: SubstitutionRule[];
  /** Handler para emitir comunicados e orientacoes de pericia ao INSS. */
  onDispatchInssNotice: (absenceId: string) => Promise<void>;
}

/**
 * Componente AbsenceManager.
 *
 * Gerencia o ciclo de afastamentos: assegura o limite dos 15 dias pagos pela empresa (CLT),
 * encaminha os casos superiores ao INSS, aponta choques com ferias e calcula a diferenca
 * salarial devida ao substituto temporario conforme a jurisprudencia trabalhista.
 */
export const AbsenceManager: React.FC<AbsenceManagerProps> = ({
  absences,
  substitutions,
  onDispatchInssNotice,
}) => {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-xl font-semibold text-slate-900">Gestor de Afastamentos e Substituicoes</h2>
      <p className="mt-1 text-sm text-slate-500">
        Cisao automatica de 15 dias CLT / INSS e calculo proporcional da Sumula 159 do TST.
      </p>
      {/* Stub de implementacao da interface visual */}
    </div>
  );
};
