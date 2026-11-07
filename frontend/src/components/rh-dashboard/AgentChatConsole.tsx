import React, { useState } from 'react';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'pulso';
  text: string;
  isRefusal?: boolean;
}

export interface AgentChatConsoleProps {
  /** Callback para envio de mensagens ao agente Pulso. */
  onSendMessage: (query: string) => Promise<{
    replyText: string;
    isRefusal: boolean;
    refusalReason?: string;
  }>;
}

/**
 * Componente AgentChatConsole.
 *
 * Console interativo do agente Pulso. Permite ao RH fazer perguntas em linguagem natural
 * sobre a saude dos times ("Como esta o time de Logistica?") e demonstra a atuacao imediata
 * do guardrail etico ao recusar consultas individuais ("Me mostra os atestados da Carla").
 */
export const AgentChatConsole: React.FC<AgentChatConsoleProps> = ({ onSendMessage }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputQuery.trim() || loading) return;

    const userText = inputQuery;
    setInputQuery('');
    setMessages((prev) => [
      ...prev,
      { id: String(Date.now()), sender: 'user', text: userText },
    ]);

    setLoading(true);
    try {
      const response = await onSendMessage(userText);
      setMessages((prev) => [
        ...prev,
        {
          id: String(Date.now() + 1),
          sender: 'pulso',
          text: response.replyText,
          isRefusal: response.isRefusal,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-[450px] flex-col rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 p-4">
        <h3 className="font-bold text-slate-800">Assistente Pulso (NR-1)</h3>
        <p className="text-xs text-slate-500">
          Analise continua de riscos psicossociais por areas e times corporativos.
        </p>
      </div>

      <div className="flex-1 space-y-3 overflow-y-auto p-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-3 text-sm ${
                msg.sender === 'user'
                  ? 'bg-indigo-600 text-white'
                  : msg.isRefusal
                    ? 'border border-amber-300 bg-amber-50 text-amber-900'
                    : 'bg-slate-100 text-slate-800'
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
      </div>

      <form onSubmit={handleSend} className="border-t border-slate-200 p-3 flex gap-2">
        <input
          type="text"
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          placeholder="Ex: Como esta o time de Logistica? ou teste: Me mostra os atestados da Carla"
          className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
        >
          Enviar
        </button>
      </form>
    </div>
  );
};
