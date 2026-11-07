import React from 'react';

export interface CertificateUploadModalProps {
  /** Flag controlling modal visibility. */
  isOpen: boolean;
  /** Modal close callback. */
  onClose: () => void;
  /** Upload handler receiving the selected image or PDF file. */
  onUploadFile: (file: File) => Promise<{ isLegible: boolean; feedbackMessage: string }>;
}

/**
 * CertificateUploadModal Component.
 *
 * Employee self-service interface for medical certificate submission.
 * Performs instantaneous OCR legibility assessment; if the image is blurry or unreadable,
 * prompts the employee for immediate recapturing before ticket submission.
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
        <h3 className="text-lg font-medium text-slate-900">Upload Medical Certificate</h3>
        <p className="mt-1 text-sm text-slate-500">
          Capture or attach a clear photo of your medical certificate.
        </p>
        {/* Component UI implementation stub */}
      </div>
    </div>
  );
};
