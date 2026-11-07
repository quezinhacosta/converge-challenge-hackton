import React from 'react';

export interface CertificateUploadModalProps {
  /** Flag de controle de visibilidade da modal. */
  isOpen: boolean;
  /** Callback para fechamento da modal. */
  onClose: () => void;
  /** Handler de envio recebendo o arquivo de imagem ou PDF do atestado. */
  onUploadFile: (file: File) => Promise<{ isLegible: boolean; feedbackMessage: string }>;
}

/**
 * Componente CertificateUploadModal.
 *
 * Interface de autoatendimento para submissao de atestado medico pelo colaborador.
 * Executa checagem de legibilidade via OCR em tempo real; se a foto estiver borrada ou
 * ilegivel, solicita imediatamente uma nova captura ao usuario antes de registrar o protocolo.
 */
export const CertificateUploadModal: React.FC<CertificateUploadModalProps> = ({
  isOpen,
  onClose,
  onUploadFile,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
        <h3 className="text-lg font-medium text-slate-900">Enviar Atestado Medico</h3>
        <p className="mt-1 text-sm text-slate-500">
          Capture ou selecione uma foto nitida do seu atestado medico.
        </p>
        {/* Stub de implementacao da interface visual */}
      </div>
    </div>
  );
};
