import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PulsoApiService } from './core/services/pulso-api.service';
import { RiskFocusCardComponent } from './features/rh-dashboard/components/risk-focus-card/risk-focus-card.component';
import { PgrInventoryTableComponent } from './features/rh-dashboard/components/pgr-inventory-table/pgr-inventory-table.component';
import { AgentChatConsoleComponent } from './features/rh-dashboard/components/agent-chat-console/agent-chat-console.component';
import { AreaSignalsViewComponent } from './features/rh-dashboard/components/area-signals-view/area-signals-view.component';
import { MicroSurveyModalComponent } from './features/employee-experience/components/micro-survey-modal/micro-survey-modal.component';
import { FeedbackDevolutivaCardComponent } from './features/employee-experience/components/feedback-devolutiva-card/feedback-devolutiva-card.component';
import { RiskCard, ResolveRiskCardPayload } from './core/models/risk-card.model';
import { PgrInventoryItem, AreaInfo } from './core/models/nr1.model';
import { AreaHistoryComparison } from './core/models/signals.model';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    RiskFocusCardComponent,
    PgrInventoryTableComponent,
    AgentChatConsoleComponent,
    AreaSignalsViewComponent,
    MicroSurveyModalComponent,
    FeedbackDevolutivaCardComponent,
  ],
  template: `
    <main class="min-h-screen bg-slate-50 text-slate-900 pb-12">
      <!-- Topbar Header -->
      <header class="border-b border-slate-200 bg-white shadow-sm">
        <div class="container mx-auto flex items-center justify-between px-6 py-4">
          <div>
            <div class="flex items-center gap-3">
              <span class="rounded-lg bg-indigo-600 px-2.5 py-1 text-sm font-black text-white tracking-wider">
                PULSO
              </span>
              <h1 class="text-xl font-bold tracking-tight text-slate-900">
                Digital Worker de Gestão de Riscos Psicossociais (NR-1)
              </h1>
            </div>
            <p class="text-xs text-slate-500 mt-0.5">
              Converge Challenge powered by Tako | Desafio Tako: Digital Workers para RH | Time Booleanas
            </p>
          </div>
          <div class="flex items-center gap-3">
            <span class="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700 border border-emerald-200">
              Vigência NR-1: 26/05/2026
            </span>
            <button
              type="button"
              (click)="isSurveyOpen = true"
              class="rounded-lg border border-indigo-200 bg-indigo-50 px-3 py-1.5 text-xs font-semibold text-indigo-700 hover:bg-indigo-100"
            >
              Simular Pesquisa Pulso (Colaborador)
            </button>
          </div>
        </div>

        <!-- Navigation Tabs -->
        <div class="container mx-auto flex gap-6 px-6 text-sm font-medium border-t border-slate-100 pt-2">
          <button
            type="button"
            (click)="activeTab = 'rh'"
            class="pb-3 border-b-2"
            [ngClass]="activeTab === 'rh' ? 'border-indigo-600 text-indigo-600 font-bold' : 'border-transparent text-slate-500 hover:text-slate-800'"
          >
            Cockpit de Governança do RH (Pontos Focais & PGR)
          </button>
          <button
            type="button"
            (click)="activeTab = 'areas'"
            class="pb-3 border-b-2"
            [ngClass]="activeTab === 'areas' ? 'border-indigo-600 text-indigo-600 font-bold' : 'border-transparent text-slate-500 hover:text-slate-800'"
          >
            Visão por Áreas & Anonimização (Guardrail &lt; 5 pessoas)
          </button>
          <button
            type="button"
            (click)="activeTab = 'colaborador'"
            class="pb-3 border-b-2"
            [ngClass]="activeTab === 'colaborador' ? 'border-indigo-600 text-indigo-600 font-bold' : 'border-transparent text-slate-500 hover:text-slate-800'"
          >
            Experiência do Colaborador (Devolutiva Transparente)
          </button>
        </div>
      </header>

      <!-- Conteudo da Tab 1: Painel do RH -->
      <div *ngIf="activeTab === 'rh'" class="container mx-auto px-6 mt-6 space-y-6">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div class="lg:col-span-2 space-y-6">
            <!-- Ponto Focal Ativo -->
            <div *ngFor="let card of activeCards">
              <app-risk-focus-card [card]="card" (resolve)="handleResolveCard($event)"></app-risk-focus-card>
            </div>
            <div *ngIf="activeCards.length === 0" class="rounded-xl border border-slate-200 bg-white p-8 text-center text-slate-500">
              Todos os pontos focais de atenção foram deliberados pelo RH.
            </div>

            <!-- Tabela do Inventario do PGR da NR-1 -->
            <app-pgr-inventory-table [items]="pgrItems" (reassess)="handleReassessItem($event)"></app-pgr-inventory-table>
          </div>

          <!-- Console do Chat com o Agente Pulso -->
          <div class="space-y-6">
            <app-agent-chat-console></app-agent-chat-console>
          </div>
        </div>
      </div>

      <!-- Conteudo da Tab 2: Visao de Areas e Anonimizacao (Caso 6) -->
      <div *ngIf="activeTab === 'areas'" class="container mx-auto px-6 mt-6 space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Area com Headcount Normal (Atendimento - 32 pessoas) -->
          <app-area-signals-view [comparison]="comparisonAtend"></app-area-signals-view>

          <!-- Area com Menos de 5 pessoas (Design - 3 pessoas) -->
          <app-area-signals-view [comparison]="comparisonDesign"></app-area-signals-view>
        </div>
      </div>

      <!-- Conteudo da Tab 3: Experiencia do Colaborador (Devolutiva) -->
      <div *ngIf="activeTab === 'colaborador'" class="container mx-auto px-6 mt-6 max-w-2xl space-y-6">
        <app-feedback-devolutiva-card
          areaName="Atendimento ao Cliente"
          summaryOfListening="Alta de atestados e horas extras após a meta de agosto, com relato de esgotamento."
          actionPlanExplanation="Revisão imediata da meta de atendimentos por hora com a liderança e abertura de círculos de escuta semanais com mediação do RH."
        ></app-feedback-devolutiva-card>
      </div>

      <!-- Modal de Pesquisa Pulso Curta (3 perguntas) -->
      <app-micro-survey-modal
        [isOpen]="isSurveyOpen"
        (close)="isSurveyOpen = false"
        (submitSurvey)="handleSurveySubmit()"
      ></app-micro-survey-modal>
    </main>
  `,
})
export class AppComponent implements OnInit {
  private readonly pulsoApi = inject(PulsoApiService);

  activeTab: 'rh' | 'areas' | 'colaborador' = 'rh';
  isSurveyOpen = false;

  activeCards: RiskCard[] = [];
  pgrItems: PgrInventoryItem[] = [];
  areas: AreaInfo[] = [];

  comparisonAtend: AreaHistoryComparison = {
    areaId: 'area_atend',
    areaName: 'Atendimento ao Cliente',
    headcount: 32,
    isAnonymized: false,
    variacaoDiasAtestadoPct: 45.0,
    variacaoHorasExtrasPct: 60.0,
    pedidosDemissaoPeriodo: 4,
    mediaEmpresaPedidosDemissao: 1.0,
    eventosContextoRecentes: ['15/08/2026: Nova meta agressiva de atendimentos por hora (+35%).'],
  };

  comparisonDesign: AreaHistoryComparison = {
    areaId: 'area_des',
    areaName: 'Design de Produto',
    headcount: 3,
    isAnonymized: true,
    variacaoDiasAtestadoPct: 0.0,
    variacaoHorasExtrasPct: 0.0,
    pedidosDemissaoPeriodo: 0,
    mediaEmpresaPedidosDemissao: 1.0,
    eventosContextoRecentes: [],
  };

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.pulsoApi.listActiveRiskCards().subscribe((cards) => {
      this.activeCards = cards;
    });

    this.pulsoApi.getPgrInventory().subscribe((items) => {
      this.pgrItems = items;
    });

    this.pulsoApi.listAreas().subscribe((areas) => {
      this.areas = areas;
    });
  }

  handleResolveCard(event: { cardId: string; payload: ResolveRiskCardPayload }): void {
    this.pulsoApi.resolveRiskCard(event.cardId, event.payload).subscribe((newItem) => {
      this.pgrItems.unshift(newItem);
      this.activeCards = this.activeCards.filter((c) => c.cardId !== event.cardId);
    });
  }

  handleReassessItem(itemId: string): void {
    this.pulsoApi.reassessPgrItem(itemId).subscribe((res) => {
      const item = this.pgrItems.find((i) => i.itemId === itemId);
      if (item && res.houveMelhora) {
        item.closureDate = new Date().toISOString().split('T')[0];
        item.closureNotes = res.parecer;
      }
    });
  }

  handleSurveySubmit(): void {
    this.isSurveyOpen = false;
    alert('Respostas anônimas registradas com sucesso! Obrigado por participar do cuidado com sua equipe.');
  }
}
