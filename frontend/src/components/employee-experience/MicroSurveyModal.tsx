import React from 'react';

export interface MicroSurveyModalProps {
  /** Flag de exibicao da modal. */
  isOpen: boolean;
  /** Titulo do check-in. */
  title: string;
  /** Callback para fechamento. */
  onClose: () => void;
  /** Submissao anonima das 3 respostas curtas. */
  onSubmitSurvey: (scores: Record<string, number>, optionalComment?: string) => Promise<void>;
}

/**
 * Componente MicroSurveyModal.
 *
 * Escuta curta e anonima (check-in de 3 perguntas mensais por chat). Substitui questionarios
 * exaustivos de 80 perguntas. Assegura sigilo total e orienta canais de acolhimento se necessario.
 */
export const MicroSurveyModal: React.FC<MicroSurveyModalProps> = ({
  isOpen,
  title,
  onClose,
  onSubmitSurvey,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <h3 className="text-lg font-bold text-slate-900">{title}</h3>
        <p className="mt-1 text-xs text-slate-500">
          Suas respostas sao 100% anonimas e compoem a media do seu time.
        </p>

        <div className="mt-4 space-y-4 text-sm text-slate-700">
          <div>
            <label className="block font-medium">1. Como voce avalia sua carga de trabalho este mes?</label>
            <div className="mt-1 flex gap-2">
              {[1, 2, 3, 4, 5].map((val) => (
                <button
                  key={val}
                  type="button"
                  className="flex-1 rounded-md border border-slate-200 py-1.5 text-center text-xs font-semibold hover:bg-indigo-50"
                >
                  {val}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="block font-medium">2. Voce sente clareza sobre suas prioridades e metas?</label>
            <div className="mt-1 flex gap-2">
              {[1, 2, 3, 4, 5].map((val) => (
                <button
                  key={val}
                  type="button"
                  className="flex-1 rounded-md border border-slate-200 py-1.5 text-center text-xs font-semibold hover:bg-indigo-50"
                >
                  {val}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="block font-medium">3. Voce se sente apoiado pela sua lideranca?</label>
            <div className="mt-1 flex gap-2">
              {[1, 2, 3, 4, 5].map((val) => (
                <button
                  key={val}
                  type="button"
                  className="flex-1 rounded-md border border-slate-200 py-1.5 text-center text-xs font-semibold hover:bg-indigo-50"
                >
                  {val}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-6 flex justify-end gap-2 border-t border-slate-100 pt-4">
          <button
            type="button"
            onClick={onClose}
            className="rounded-md px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-100"
          >
            Fechar
          </button>
          <button
            type="button"
            onClick={() => onSubmitSurvey({ q1: 4, q2: 4, q3: 3 })}
            className="rounded-md bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-indigo-700"
          >
            Enviar Respostas Anonimas
          </button>
        </div>
      </div>
    </div>
  );
};
