import React from 'react';
import { RiskFocusCard } from '@/components/rh-dashboard/RiskFocusCard';
import { PgrInventoryTable } from '@/components/rh-dashboard/PgrInventoryTable';
import { AgentChatConsole } from '@/components/rh-dashboard/AgentChatConsole';

/**
 * Pagina inicial do console do Pulso para o RH.
 */
export default function PulsoDashboardPage() {
  const demoCard = {
    cardId: 'card-atend-01',
    areaId: 'area-atend',
    areaName: 'Atendimento ao Cliente',
    areaHeadcount: 32,
    riskLevel: 'VERMELHO' as const,
    fatorRiscoProvavel: 'SOBRECARGA_METAS' as const,
    oQueMudouUltimosMeses:
      'dias de atestado +45%, horas extras +60%, 4 pedidos de demissao (media da empresa: 1), nota de carga de trabalho na pesquisa pulso caiu de 3,9 para 2,4.',
    contextoOrganizacional:
      'a alta comeca 2 semanas depois da nova meta de atendimentos por hora (implantada em agosto).',
    acaoSugerida:
      'revisar a meta com a lideranca, conversa de escuta com o time mediada pelo RH, incluir o risco no inventario do PGR com reavaliacao em 60 dias.',
    fontesConsultadas: [
      'ponto',
      'folha',
      'desligamentos',
      'pesquisa pulso de outubro',
    ],
    status: 'ABERTO' as const,
    createdAt: new Date().toISOString(),
  };

  return (
    <main className="container mx-auto p-6 space-y-6">
      <header className="border-b border-slate-200 pb-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">
              Pulso | Gestao de Riscos Psicossociais (NR-1)
            </h1>
            <p className="text-sm text-slate-600">
              Converge Challenge powered by Tako | Desafio Tako: Digital Workers para RH | Time Booleanas
            </p>
          </div>
          <span className="rounded-full bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700 border border-indigo-200">
            Vigencia NR-1: Maio/2026
          </span>
        </div>
      </header>

      {/* Grid Principal do RH */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <RiskFocusCard card={demoCard} onResolve={async () => {}} />
          <PgrInventoryTable items={[]} onReassess={async () => {}} />
        </div>
        <div className="space-y-6">
          <AgentChatConsole
            onSendMessage={async (query) => {
              if (query.toLowerCase().includes('carla')) {
                return {
                  replyText:
                    'O Pulso opera exclusivamente no nivel de areas e times para gestao de riscos da NR-1. Em conformidade com a LGPD e as diretrizes eticas do Desafio Tako, informacoes individuais de saude nao sao consultadas nem exibidas.',
                  isRefusal: true,
                  refusalReason: 'LGPD / Guardrail Etico',
                };
              }
              return {
                replyText:
                  'O time de Logistica apresenta estabilidade operacional no ponto e folha, com sinal amarelo recente decorrente de troca de lideranca em setembro.',
                isRefusal: false,
                sourcesUsed: ['ponto', 'folha', 'eventos_contexto'],
              };
            }}
          />
        </div>
      </section>
    </main>
  );
}
