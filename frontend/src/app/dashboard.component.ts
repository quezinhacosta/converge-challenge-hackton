import { Component, OnInit, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { PulsoApiService, ChatResponse } from './core/services/pulso-api.service';
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
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    RiskFocusCardComponent,
    PgrInventoryTableComponent,
    AgentChatConsoleComponent,
    AreaSignalsViewComponent,
    MicroSurveyModalComponent,
    FeedbackDevolutivaCardComponent,
  ],
  template: `
    <div class="min-h-screen bg-slate-50/70 text-slate-900 flex flex-col font-sans">
      <div role="status" class="px-6 py-2 text-sm bg-amber-50 text-amber-950">
        {{ apiState() }} <a routerLink="/conhecimento" class="underline ml-4">Base de conhecimento</a>
      </div>
      <!-- Topbar Principal com Identidade Visual & Metadados do Hackathon -->
      <header class="border-b border-slate-200 bg-white shadow-xs sticky top-0 z-40">
        <div class="container mx-auto flex flex-wrap items-center justify-between px-6 py-3.5 gap-4">
          <!-- Logo & Nome do Produto -->
          <div class="flex items-center gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-700 to-indigo-500 text-white shadow-sm ring-4 ring-indigo-50">
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
            </div>
            <div>
              <div class="flex items-center gap-2">
                <span class="rounded bg-indigo-600 px-2 py-0.5 text-[11px] font-black text-white tracking-widest uppercase">
                  VytAI
                </span>
                <span class="text-xs font-semibold text-slate-500">v1.2 &bull; Powered by Tako</span>
              </div>
              <h1 class="text-sm sm:text-base font-bold tracking-tight text-slate-900 mt-0.5">
                Digital Worker de Gestão de Riscos Psicossociais (NR-1)
              </h1>
            </div>
          </div>

          <!-- Metadados de Compliance & Ações Globais -->
          <div class="flex items-center gap-2.5">
            <span class="hidden sm:inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-3 py-1 text-xs font-bold text-emerald-800 border border-emerald-200">
              <span class="h-2 w-2 rounded-full bg-emerald-500"></span>
              Vigência NR-1: 26/05/2026
            </span>
            <button
              type="button"
              (click)="isSurveyOpen = true"
              class="inline-flex items-center gap-1.5 rounded-xl border border-indigo-200 bg-indigo-50/70 px-3.5 py-1.5 text-xs font-bold text-indigo-700 hover:bg-indigo-100 hover:text-indigo-800 transition-colors shadow-xs"
            >
              <svg class="h-4 w-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
              </svg>
              Simular Pesquisa VytAI (Colaborador)
            </button>
          </div>
        </div>

        <!-- Barra de Indicadores Macro (Estatísticas do Cockpit) -->
        <div class="border-t border-slate-100 bg-slate-50/90 py-2.5 px-6">
          <div class="container mx-auto flex flex-wrap items-center justify-between gap-4 text-xs">
            <div class="flex flex-wrap items-center gap-6">
              <div class="flex items-center gap-2">
                <span class="text-slate-500">Colaboradores Monitorados:</span>
                <span class="font-bold font-mono text-slate-900">{{ totalPeople() === null ? '—' : totalPeople() }}</span>
              </div>
              <div class="flex items-center gap-2">
                <span class="text-slate-500">Áreas Mapeadas:</span>
                <span class="font-bold font-mono text-slate-900">{{ areaCount() === null ? '—' : areaCount() }}</span>
              </div>
              <div class="flex items-center gap-2">
                <span class="text-slate-500">Pontos Focais de Atenção:</span>
                <span class="inline-flex items-center gap-1 rounded-full bg-rose-100 px-2 py-0.2 font-bold font-mono text-rose-700">
                  <span class="h-1.5 w-1.5 rounded-full bg-rose-600 animate-pulse"></span>
                  {{ activeCards.length }} áreas
                </span>
              </div>
              <div class="flex items-center gap-2">
                <span class="text-slate-500">Conformidade NR-1 / PGR:</span>
                <span class="font-bold font-mono text-emerald-700">Revisão humana necessária</span>
              </div>
              <div class="flex items-center gap-2">
                <span class="text-slate-500">Guardrails LGPD:</span>
                <span class="inline-flex items-center gap-1 text-emerald-700 font-semibold">
                  <svg class="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                  </svg>
                  Proteção por área
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Seletor Rápido dos 7 Cenários do Pitch -->
        <div *ngIf="demoMode()" class="border-t border-slate-200/60 bg-white py-2 px-6">
          <div class="container mx-auto flex items-center gap-2 overflow-x-auto text-xs py-0.5">
            <span class="font-bold text-[11px] text-slate-500 shrink-0 uppercase tracking-wider">
              Atalhos dos 7 Cenários:
            </span>
            <button
              *ngFor="let sc of pitchScenarios"
              type="button"
              (click)="selectScenario(sc.id)"
              class="shrink-0 rounded-lg px-2.5 py-1 text-xs font-semibold transition-all"
              [ngClass]="activeScenario() === sc.id ? 'bg-indigo-600 text-white shadow-xs' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'"
            >
              {{ sc.title }}
            </button>
          </div>
        </div>

        <!-- Abas de Navegação -->
        <nav class="container mx-auto flex gap-8 px-6 text-xs sm:text-sm font-semibold border-t border-slate-100">
          <button
            type="button"
            (click)="activeTab = 'rh'"
            class="py-3 border-b-2 transition-all flex items-center gap-2"
            [ngClass]="activeTab === 'rh' ? 'border-indigo-600 text-indigo-600 font-bold' : 'border-transparent text-slate-500 hover:text-slate-800'"
          >
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
            </svg>
            Cockpit de Governança RH (Pontos Focais & PGR)
          </button>
          <button
            type="button"
            (click)="activeTab = 'areas'"
            class="py-3 border-b-2 transition-all flex items-center gap-2"
            [ngClass]="activeTab === 'areas' ? 'border-indigo-600 text-indigo-600 font-bold' : 'border-transparent text-slate-500 hover:text-slate-800'"
          >
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
            </svg>
            Visão por Áreas
          </button>
          <button
            type="button"
            (click)="activeTab = 'colaborador'"
            class="py-3 border-b-2 transition-all flex items-center gap-2"
            [ngClass]="activeTab === 'colaborador' ? 'border-indigo-600 text-indigo-600 font-bold' : 'border-transparent text-slate-500 hover:text-slate-800'"
          >
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
            </svg>
            Experiência do Colaborador (Devolutiva Transparente)
          </button>
        </nav>
      </header>

      <!-- Conteúdo Principal Dinâmico por Aba -->
      <main class="container mx-auto px-6 py-6 flex-1">
        <!-- Notificação de Ação Executada com Sucesso -->
        <div
          *ngIf="actionSuccessMessage()"
          class="mb-6 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-xs font-bold text-emerald-900 flex items-center justify-between shadow-xs animate-fadeIn"
        >
          <div class="flex items-center gap-2">
            <svg class="h-5 w-5 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
            </svg>
            <span>{{ actionSuccessMessage() }}</span>
          </div>
          <button type="button" (click)="actionSuccessMessage.set(null)" class="text-emerald-700 hover:text-emerald-900">
            &times;
          </button>
        </div>

        <!-- ABA 1: Cockpit do RH (Pontos Focais Ativos, PGR e Chat Copilot) -->
        <section *ngIf="activeTab === 'rh'" class="space-y-6">
          <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <!-- Coluna Esquerda: Cards de Ponto Focal e Inventário PGR (8 colunas) -->
            <div class="lg:col-span-7 xl:col-span-8 space-y-6">
              <!-- Seção de Pontos Focais de Atenção (Cards Vermelho e Amarelo) -->
              <div class="space-y-4">
                <div class="flex items-center justify-between">
                  <div>
                    <h2 class="text-lg font-bold text-slate-900 flex items-center gap-2">
                      Pontos Focais de Atenção do RH
                      <span class="rounded-full bg-rose-100 px-2.5 py-0.5 text-xs font-bold text-rose-700">
                        {{ activeCards.length }} Pendentes
                      </span>
                    </h2>
                    <p class="text-xs text-slate-500">
                      O Digital Worker correlaciona ponto, folha, turnover e pesquisa pulso gerando recomendações prontas para deliberação humana.
                    </p>
                  </div>
                </div>

                <!-- Lista de Cards Ativos -->
                <div *ngFor="let card of activeCards" class="space-y-4">
                  <app-risk-focus-card [card]="card" (resolve)="handleResolveCard($event)"></app-risk-focus-card>
                </div>

                <div
                  *ngIf="activeCards.length === 0"
                  class="rounded-2xl border border-slate-200 bg-white p-8 text-center text-slate-500 space-y-2 shadow-xs"
                >
                  <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600">
                    <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                    </svg>
                  </div>
                  <h4 class="text-sm font-bold text-slate-800">Todos os pontos focais foram deliberados</h4>
                  <p class="text-xs text-slate-500">
                    Os planos aprovados constam no Inventário do PGR abaixo para acompanhamento dos ciclos de 60 dias.
                  </p>
                </div>
              </div>

              <!-- Tabela do Inventário do PGR (NR-1 Oficial) -->
              <app-pgr-inventory-table
                [items]="pgrItems"
                (reassess)="handleReassessItem($event)"
              ></app-pgr-inventory-table>
            </div>

            <!-- Coluna Direita: Copilot Assistente VytAI (4 colunas) -->
            <div class="lg:col-span-5 xl:col-span-4 space-y-6">
              <app-agent-chat-console></app-agent-chat-console>
            </div>
          </div>
        </section>

        <!-- ABA 2: Visão de Áreas & Anonimização (LGPD) -->
        <section *ngIf="activeTab === 'areas'" class="space-y-6">
          <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs space-y-4">
            <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-4">
              <div>
                <h2 class="text-lg font-bold text-slate-900">
                  Explorador de Áreas & Proteção de Anonimato
                </h2>
                <p class="text-xs text-slate-500">
                  Validação do guardrail ético: equipes com menos de 5 colaboradores têm seus dados ocultados automaticamente.
                </p>
              </div>

              <!-- Seletor de Áreas -->
              <div class="flex flex-wrap items-center gap-1.5">
                <button
                  *ngFor="let a of availableAreas"
                  type="button"
                  (click)="loadAreaSignals(a.id)"
                  class="rounded-xl px-3 py-1.5 text-xs font-semibold transition-all"
                  [ngClass]="selectedAreaId() === a.id ? 'bg-indigo-600 text-white shadow-xs' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'"
                >
                  {{ a.name }} ({{ a.headcount }}p)
                </button>
              </div>
            </div>

            <!-- Visualização da Área Selecionada -->
            <div *ngIf="currentComparison()" class="pt-2">
              <app-area-signals-view [comparison]="currentComparison()!"></app-area-signals-view>
            </div>
          </div>
        </section>

        <!-- ABA 3: Experiência do Colaborador (Devolutiva Transparente) -->
        <section *ngIf="activeTab === 'colaborador'" class="max-w-3xl mx-auto space-y-6">
          <div class="text-center space-y-1">
            <h2 class="text-xl font-bold text-slate-900">Portal de Transparência e Escuta da Equipe</h2>
            <p class="text-xs text-slate-500">
              O colaborador é comunicado sobre as ações tomadas a partir de suas respostas, fechando o ciclo de confiança.
            </p>
          </div>

          <app-feedback-devolutiva-card
            areaName="Atendimento ao Cliente"
            summaryOfListening="Queda expressiva na nota de equilíbrio de carga de trabalho e sobrecarga de horas extras relatadas na pesquisa de pulso de outubro."
            actionPlanExplanation="Revisão imediata da meta de atendimentos por hora junto à diretoria, redistribuição das filas de chamados e círculos de escuta semanais com mediação do RH."
          ></app-feedback-devolutiva-card>

          <!-- Chamada para a Pesquisa VytAI -->
          <div class="rounded-2xl border border-indigo-200 bg-indigo-50/70 p-6 flex flex-wrap items-center justify-between gap-4">
            <div>
              <h3 class="text-sm font-bold text-indigo-900">Check-in Mensal Aberto</h3>
              <p class="text-xs text-indigo-700 mt-0.5">
                Compartilhe sua percepção sobre ritmo e apoio da liderança. 100% anônimo.
              </p>
            </div>
            <button
              type="button"
              (click)="isSurveyOpen = true"
              class="rounded-xl bg-indigo-600 px-4 py-2.5 text-xs font-bold text-white shadow-xs hover:bg-indigo-700 active:scale-95 transition-all"
            >
              Responder Check-in de 30s
            </button>
          </div>
        </section>
      </main>

      <!-- Rodapé Institucional -->
      <footer class="border-t border-slate-200 bg-white py-4 text-center text-xs text-slate-500">
        <div class="container mx-auto px-6 flex flex-wrap items-center justify-between gap-3">
          <span>&copy; 2026 VytAI &bull; Gestão de Riscos Psicossociais (NR-1 / Portaria MTE nº 1.419/2024)</span>
          <span class="font-mono text-[11px] text-slate-400">Powered by Tako &bull; Converge Challenge Hackathon</span>
        </div>
      </footer>

      <!-- Modal de Pesquisa VytAI do Colaborador -->
      <app-micro-survey-modal
        [isOpen]="isSurveyOpen"
        (close)="isSurveyOpen = false"
        (submitSurvey)="handleSurveySubmit()"
      ></app-micro-survey-modal>
    </div>
  `,
})
export class DashboardComponent implements OnInit {
  private readonly pulsoApi = inject(PulsoApiService);

  activeTab: 'rh' | 'areas' | 'colaborador' = 'rh';
  isSurveyOpen = false;
  actionSuccessMessage = signal<string | null>(null);

  activeCards: RiskCard[] = [];
  pgrItems: PgrInventoryItem[] = [];

  availableAreas = [
    { id: 'area_atend', name: 'Atendimento ao Cliente', headcount: 32 },
    { id: 'area_log', name: 'Logística', headcount: 28 },
    { id: 'area_vend', name: 'Vendas', headcount: 35 },
    { id: 'area_fin', name: 'Financeiro', headcount: 18 },
    { id: 'area_des', name: 'Design de Produto (N<5)', headcount: 3 },
  ];

  selectedAreaId = signal<string>('area_atend');
  currentComparison = signal<AreaHistoryComparison | null>(null);

  activeScenario = signal<string>('c2');

  pitchScenarios = [
    { id: 'c1', title: '1. Financeiro Estável' },
    { id: 'c2', title: '2. Atendimento (Card Vermelho)' },
    { id: 'c3', title: '3. Logística (Troca Gestor)' },
    { id: 'c4', title: '4. Vendas (Denúncias Compliance)' },
    { id: 'c5', title: '5. Guardrail: Atestados da Carla' },
    { id: 'c6', title: '6. Design (Quórum < 5p)' },
    { id: 'c7', title: '7. Reavaliação 60d (Eficaz)' },
  ];

  demoMode = signal(false);
  apiState = signal('Verificando conexão...');
  totalPeople = signal<number | null>(null);
  areaCount = signal<number | null>(null);
  private reportError = () => this.apiState.set('Dados indisponíveis. Verifique sua autenticação e a conexão com a API.');

  ngOnInit(): void {
    this.pulsoApi.health().subscribe({ next: status => {
      this.demoMode.set(status.mode === 'demo');
      this.apiState.set(status.mode === 'demo' ? 'Demonstração: dados sintéticos.' : 'Ambiente autenticado. Confira a origem e o período dos indicadores.');
    }, error: this.reportError });
    this.pulsoApi.listAreas().subscribe({next: areas => {
      this.areaCount.set(areas.length);
      this.totalPeople.set(areas.reduce((sum, a) => sum + a.headcount, 0));
    }, error: this.reportError });
    this.loadInitialData();
  }

  loadInitialData(): void {
    this.pulsoApi.listActiveRiskCards().subscribe({next: cards => { this.activeCards = cards; }, error: this.reportError});

    this.pulsoApi.getPgrInventory().subscribe({next: items => { this.pgrItems = items; }, error: this.reportError});

    this.loadAreaSignals('area_atend');
  }

  loadAreaSignals(areaId: string): void {
    this.selectedAreaId.set(areaId);
    this.currentComparison.set(null);
    this.pulsoApi.getAreaSignals(areaId).subscribe({next: comp => { this.currentComparison.set(comp); }, error: this.reportError});
  }

  selectScenario(scenarioId: string): void {
    this.activeScenario.set(scenarioId);

    switch (scenarioId) {
      case 'c1':
        // Financeiro Estável
        this.activeTab = 'areas';
        this.loadAreaSignals('area_fin');
        break;
      case 'c2':
        // Atendimento (Card Vermelho)
        this.activeTab = 'rh';
        break;
      case 'c3':
        // Logística (Troca de Gestor)
        this.activeTab = 'rh';
        break;
      case 'c4':
        // Vendas (Denúncias Compliance)
        this.activeTab = 'areas';
        this.loadAreaSignals('area_vend');
        break;
      case 'c5':
        // Guardrail Carla
        this.activeTab = 'rh';
        break;
      case 'c6':
        // Design (Quórum < 5p)
        this.activeTab = 'areas';
        this.loadAreaSignals('area_des');
        break;
      case 'c7':
        // Reavaliação 60d
        this.activeTab = 'rh';
        break;
    }
  }

  handleResolveCard(event: { cardId: string; payload: ResolveRiskCardPayload }): void {
    this.pulsoApi.resolveRiskCard(event.cardId, event.payload).subscribe({
      next: (newItem) => {
        this.activeCards = this.activeCards.filter(c => c.cardId !== event.cardId);
        if (event.payload.actionType === 'DESCARTAR') {
          this.actionSuccessMessage.set('Card descartado. Nenhum item foi acrescentado ao PGR.');
        } else {
          this.pgrItems = [newItem, ...this.pgrItems];
          this.actionSuccessMessage.set('Decisão registrada no PGR.');
        }
      },
      error: () => this.actionSuccessMessage.set('Não foi possível confirmar a decisão. Atualize o painel antes de tentar novamente.'),
    });
  }

  handleReassessItem(itemId: string): void {
    this.pulsoApi.reassessPgrItem(itemId).subscribe({ next: (res) => {
      this.actionSuccessMessage.set(
        res.parecer
      );
    }, error: () => this.actionSuccessMessage.set('Reavaliação indisponível. Nenhuma melhora foi registrada.') });
  }

  handleSurveySubmit(): void {
    this.actionSuccessMessage.set(
      'Demonstração: o envio da pesquisa ainda não está integrado.'
    );
  }
}
