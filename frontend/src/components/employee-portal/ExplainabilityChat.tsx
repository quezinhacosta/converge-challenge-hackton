import React from 'react';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'agent';
  content: string;
  timestamp: string;
}

export interface ExplainabilityChatProps {
  /** Historico de mensagens trocadas entre o colaborador e a IA do PayTrust. */
  messages: ChatMessage[];
  /** Callback para envio de duvidas sobre descontos, adicionais ou afastamentos. */
  onSendMessage: (query: string) => Promise<void>;
  /** Indica se o agente esta processando a resposta. */
  isLoading: boolean;
}

/**
 * Componente ExplainabilityChat.
 *
 * Widget conversacional integrado ao Portal do Colaborador. Esclarece duvidas sobre
 * lancamentos da folha, base de calculo de ferias e status de afastamentos, eliminando
 * o volume excessivo de chamados recorrentes recebidos pelo DP no fechamento do mes.
 */
export const ExplainabilityChat: React.FC<ExplainabilityChatProps> = ({
  messages,
  onSendMessage,
  isLoading,
}) => {
  return (
    <div className="flex flex-col h-[500px] rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 p-4">
        <h3 className="font-semibold text-slate-800">Assistente PayTrust</h3>
        <p className="text-xs text-slate-500">Tire suas duvidas sobre seu holerite e beneficios.</p>
      </div>
      {/* Stub de implementacao da interface visual */}
    </div>
  );
};
