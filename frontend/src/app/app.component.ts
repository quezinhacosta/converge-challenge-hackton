import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RiskFocusCardComponent } from './features/rh-dashboard/components/risk-focus-card/risk-focus-card.component';
import { PgrInventoryTableComponent } from './features/rh-dashboard/components/pgr-inventory-table/pgr-inventory-table.component';
import { AgentChatConsoleComponent } from './features/rh-dashboard/components/agent-chat-console/agent-chat-console.component';
import { RiskCard, ResolveRiskCardPayload } from './core/models/risk-card.model';
import { PgrInventoryItem } from './core/models/nr1.model';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    RiskFocusCardComponent,
    PgrInventoryTableComponent,
    AgentChatConsoleComponent,
  ],
  template: `
    <main class="container mx-auto p-6 space-y-6">
      <header class="border-b border-slate-200 pb-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold tracking-tight text-slate-900">
              Pulso | Gestão de Riscos Psicossociais (NR-1)
            </h1>
            <p class="text-sm text-slate-600">
              Converge Challenge powered by Tako | Desafio Tako: Digital Workers para RH | Time Booleanas
            </p>
          </div>
          <span
            class="rounded-full bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700 border border-indigo-200"
          >
            Vigência NR-1: Maio/2026
          </span>
        </div>
      </header>

      <!-- Grid Principal do RH -->
      <section class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 space-y-6">
          <app-risk-focus-card [card]="demoCard" (resolve)="handleResolve($event)"></app-risk-focus-card>
          <app-pgr-inventory-table [items]="pgrItems" (reassess)="handleReassess($event)"></app-pgr-inventory-table>
        </div>
        <div class="space-y-6">
          <app-agent-chat-console></app-agent-chat-console>
        </div>
      </section>
    </main>
  `,
})
export class AppComponent {
  demoCard: RiskCard = {
    cardId: 'card-atend-01',
    areaId: 'area-atend',
    areaName: 'Atendimento ao Cliente',
    areaHeadcount: 32,
    riskLevel: 'VERMELHO',
    fatorRiscoProvavel: 'SOBRECARGA_METAS',
    oQueMudouUltimosMeses:
      'dias de atestado +45%, horas extras +60%, 4 pedidos de demissão (média da empresa: 1), nota de carga de trabalho na pesquisa pulso caiu de 3,9 para 2,4.',
    contextoOrganizacional:
      'a alta começa 2 semanas depois da nova meta de atendimentos por hora (implantada em agosto).',
    acaoSugerida:
      'revisar a meta com a liderança, conversa de escuta com o time mediada pelo RH, incluir o risco no inventário do PGR com reavaliação em 60 dias.',
    fontesConsultadas: ['ponto', 'folha', 'desligamentos', 'pesquisa pulso de outubro'],
    status: 'ABERTO',
    createdAt: new Date().toISOString(),
  };

  pgrItems: PgrInventoryItem[] = [];

  handleResolve(event: { cardId: string; payload: ResolveRiskCardPayload }): void {
    if (event.payload.actionType === 'APROVAR_PGR') {
      this.pgrItems.push({
        itemId: 'pgr-01',
        areaId: this.demoCard.areaId,
        areaName: this.demoCard.areaName,
        factor: this.demoCard.fatorRiscoProvavel,
        severityLevel: this.demoCard.riskLevel,
        actionPlanDescription: this.demoCard.acaoSugerida,
        responsiblePerson: event.payload.reviewerName,
        deadlineDate: '2026-12-15',
        reassessmentIntervalDays: 60,
        registeredAt: new Date().toISOString(),
        isReopened: false,
        auditLog: ['Aprovado em 1 clique pelo RH no card card-atend-01'],
      });
      this.demoCard.status = 'APROVADO_PGR';
    }
  }

  handleReassess(itemId: string): void {
    const item = this.pgrItems.find((i) => i.itemId === itemId);
    if (item) {
      item.closureDate = new Date().toISOString().split('T')[0];
      item.closureNotes = 'Indicadores melhoraram (queda de 35% nos atestados); ciclo encerrado com sucesso.';
    }
  }
}
