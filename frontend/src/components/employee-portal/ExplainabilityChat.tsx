import React from 'react';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'agent';
  content: string;
  timestamp: string;
}

export interface ExplainabilityChatProps {
  /** Chat history between the collaborator and the PayTrust Compliance Agent. */
  messages: ChatMessage[];
  /** Handler to send collaborator questions regarding deductions, overtime, or leaves. */
  onSendMessage: (query: string) => Promise<void>;
  /** Indicates whether the agent is generating a response. */
  isLoading: boolean;
}

/**
 * ExplainabilityChat Component.
 *
 * Conversational AI widget embedded inside the Employee Portal. Answers employee
 * inquiries about payroll lines, vacation pay calculations, and medical leave status,
 * eliminating the typical surge of DP support tickets during payroll week.
 */
export const ExplainabilityChat: React.FC<ExplainabilityChatProps> = ({
  messages,
  onSendMessage,
  isLoading,
}) => {
  return (
    <div className="flex flex-col h-[500px] rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 p-4">
        <h3 className="font-semibold text-slate-800">PayTrust Assistant</h3>
        <p className="text-xs text-slate-500">Ask questions about your paystub and benefits.</p>
      </div>
      {/* Component UI implementation stub */}
    </div>
  );
};
