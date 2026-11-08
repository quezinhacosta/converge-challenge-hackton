import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PulsoApiService } from './core/services/pulso-api.service';
import { RiskFocusCardComponent } from './features/rh-dashboard/components/risk-focus-card/risk-focus-card.component';
import { PgrInventoryTableComponent } from './features/rh-dashboard/components/pgr-inventory-table/pgr-inventory-table.component';
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
    AreaSignalsViewComponent,
    MicroSurveyModalComponent,
    FeedbackDevolutivaCardComponent,
  ],
  template: `
    <div class="min-h-screen bg-black text-zinc-100 flex flex-row font-sans antialiased">
      <!-- Barra Lateral Esquerda (Navegação Vertical) -->
      <aside class="w-64 shrink-0 bg-zinc-950 border-r border-zinc-800 flex flex-col justify-between h-screen sticky top-0 z-30 select-none">
        <div class="flex flex-col h-full overflow-y-auto">
          <!-- Cabeçalho / Logo vitAI -->
          <div class="p-5 border-b border-zinc-800/80">
            <div class="flex items-center gap-2.5">
              <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-zinc-900 border border-zinc-700 text-white font-bold text-sm">
                V
              </div>
              <div>
                <div class="flex items-center gap-1.5">
                  <span class="text-base font-bold tracking-tight text-white">
                    vit<span class="text-zinc-400">AI</span>
                  </span>
                  <span class="rounded bg-zinc-800 px-1.5 py-0.2 text-[10px] font-mono text-zinc-400 border border-zinc-700">
                    NR-1
                  </span>
                </div>
                <p class="text-[11px] text-zinc-500 font-medium">Governança Psicossocial</p>
              </div>
            </div>

            <!-- Status do Motor -->
            <div class="mt-3.5 flex items-center gap-2 rounded-md bg-zinc-900/80 border border-zinc-800 px-2.5 py-1.5 text-[11px] text-zinc-400 font-mono">
              <span class="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
              <span>Motor Ativo (XGBoost)</span>
            </div>
          </div>

          <!-- Navegação Principal -->
          <nav class="p-3 space-y-1">
            <div class="px-2 pb-1 text-[10px] font-mono font-semibold uppercase tracking-wider text-zinc-500">
              Módulos
            </div>

            <button
              type="button"
              (click)="activeTab = 'rh'"
              class="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition-colors text-left"
              [ngClass]="activeTab === 'rh' ? 'bg-zinc-800 text-white font-semibold border border-zinc-700' : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/60'"
            >
              <svg class="h-4 w-4 shrink-0 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
              </svg>
              <span>Cockpit Executivo</span>
            </button>

            <button
              type="button"
              (click)="activeTab = 'areas'"
              class="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition-colors text-left"
              [ngClass]="activeTab === 'areas' ? 'bg-zinc-800 text-white font-semibold border border-zinc-700' : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/60'"
            >
              <svg class="h-4 w-4 shrink-0 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
              </svg>
              <span>Matriz de Áreas (Shield LGPD)</span>
            </button>

            <button
              type="button"
              (click)="activeTab = 'colaborador'"
              class="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition-colors text-left"
              [ngClass]="activeTab === 'colaborador' ? 'bg-zinc-800 text-white font-semibold border border-zinc-700' : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/60'"
            >
              <svg class="h-4 w-4 shrink-0 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
              </svg>
              <span>Devolutiva ao Time</span>
            </button>
          </nav>

          <!-- Cenários de Teste / Pitch (Em lista vertical organizada) -->
          <div class="p-3 border-t border-zinc-800/80">
            <div class="px-2 pb-2 text-[10px] font-mono font-semibold uppercase tracking-wider text-zinc-500">
              Cenários de Validação
            </div>
            <div class="space-y-1">
              <button
                *ngFor="let sc of pitchScenarios"
                type="button"
                (click)="selectScenario(sc.id)"
                class="w-full text-left px-2.5 py-1.5 rounded-md text-[11px] font-mono transition-colors"
                [ngClass]="activeScenario() === sc.id ? 'bg-zinc-800 text-zinc-100 font-semibold border border-zinc-700' : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/60'"
              >
                {{ sc.title }}
              </button>
            </div>
          </div>

          <!-- Ação Inferior da Barra Lateral -->
          <div class="mt-auto p-4 border-t border-zinc-800/80 space-y-2">
            <button
              type="button"
              (click)="isSurveyOpen = true"
              class="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 px-3 py-2 text-xs font-semibold text-zinc-200 transition-colors"
            >
              <svg class="h-4 w-4 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
              </svg>
              Simular Pesquisa Pulso
            </button>
            <p class="text-[10px] text-zinc-500 font-mono text-center">
              Portaria MTE nº 1.419/2024
            </p>
          </div>
        </div>
      </aside>

      <!-- Conteúdo Principal à Direita -->
      <main class="flex-1 bg-zinc-950/40 min-h-screen overflow-y-auto flex flex-col">
        <!-- Topo da Área de Conteúdo -->
        <header class="border-b border-zinc-800/80 bg-zinc-950/60 backdrop-blur-md px-8 py-4 flex items-center justify-between sticky top-0 z-20">
          <div>
            <h1 class="text-base font-semibold text-white">
              {{ activeTab === 'rh' ? 'Cockpit de Governança Executiva' : (activeTab === 'areas' ? 'Matriz de Áreas & Shield LGPD' : 'Devolutiva de Escuta ao Time') }}
            </h1>
            <p class="text-xs text-zinc-400">
              Auditoria contínua e mitigação de fatores de risco psicossocial conforme a NR-1.
            </p>
          </div>

          <div class="flex items-center gap-2">
            <span class="inline-flex items-center gap-1.5 rounded-md bg-zinc-900 border border-zinc-800 px-2.5 py-1 text-xs font-mono text-zinc-300">
              Portaria MTE 1.419/2024
            </span>
          </div>
        </header>

        <!-- Corpo da Página -->
        <div class="p-8 space-y-6 max-w-7xl w-full mx-auto flex-1">
          <!-- Mensagem de Sucesso de Ação -->
          <div
            *ngIf="actionSuccessMessage()"
            class="rounded-lg border border-emerald-500/30 bg-emerald-950/20 p-3.5 text-xs font-mono text-emerald-300 flex items-center justify-between"
          >
            <div class="flex items-center gap-2">
              <svg class="h-4 w-4 text-emerald-400 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
              </svg>
              <span>{{ actionSuccessMessage() }}</span>
            </div>
            <button type="button" (click)="actionSuccessMessage.set(null)" class="text-zinc-400 hover:text-white text-base">
              &times;
            </button>
          </div>

          <!-- Indicadores Executivos Principais (4 KPIs Sóbrios) -->
          <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div class="rounded-xl border border-zinc-800 bg-zinc-900/40 p-4">
              <div class="flex items-center justify-between text-xs text-zinc-400">
                <span>Vidas Monitoradas</span>
                <span class="text-[10px] font-mono text-zinc-500">Folha / Ponto</span>
              </div>
              <div class="mt-2 flex items-baseline gap-1.5">
                <span class="text-2xl font-bold font-mono text-white">154</span>
                <span class="text-xs text-zinc-400">colaboradores</span>
              </div>
              <p class="text-[11px] text-zinc-500 mt-1">Efetivo integralmente rastreado</p>
            </div>

            <div class="rounded-xl border border-zinc-800 bg-zinc-900/40 p-4">
              <div class="flex items-center justify-between text-xs text-zinc-400">
                <span>Áreas Mapeadas</span>
                <span class="text-[10px] font-mono text-zinc-500">Quórum</span>
              </div>
              <div class="mt-2 flex items-baseline gap-1.5">
                <span class="text-2xl font-bold font-mono text-white">7</span>
                <span class="text-xs text-zinc-400">setores (1 com shield)</span>
              </div>
              <p class="text-[11px] text-zinc-500 mt-1">Design (3p) resguardado por sigilo</p>
            </div>

            <div class="rounded-xl border border-zinc-800 bg-zinc-900/40 p-4">
              <div class="flex items-center justify-between text-xs text-zinc-400">
                <span>Pontos Focais de Risco</span>
                <span class="text-[10px] font-mono text-zinc-500">Aguardando Aval</span>
              </div>
              <div class="mt-2 flex items-baseline gap-1.5">
                <span class="text-2xl font-bold font-mono" [ngClass]="activeCards.length > 0 ? 'text-rose-400' : 'text-zinc-100'">
                  {{ activeCards.length }}
                </span>
                <span class="text-xs text-zinc-400">pendências</span>
              </div>
              <p class="text-[11px] text-zinc-500 mt-1">Atendimento ao Cliente e Logística</p>
            </div>

            <div class="rounded-xl border border-zinc-800 bg-zinc-900/40 p-4">
              <div class="flex items-center justify-between text-xs text-zinc-400">
                <span>Conformidade PGR</span>
                <span class="text-[10px] font-mono text-emerald-400">Auditável</span>
              </div>
              <div class="mt-2 flex items-baseline gap-1.5">
                <span class="text-2xl font-bold font-mono text-emerald-400">94.2%</span>
                <span class="text-xs text-zinc-400">índice de cobertura</span>
              </div>
              <p class="text-[11px] text-zinc-500 mt-1">Planos alinhados à Portaria MTE</p>
            </div>
          </section>

          <!-- ABA 1: Cockpit Executivo (Ponto Focal + Tabela PGR) -->
          <section *ngIf="activeTab === 'rh'" class="space-y-6">
            <!-- Ponto Focal Principal -->
            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <div>
                  <h2 class="text-sm font-semibold text-white uppercase tracking-wider text-zinc-300">
                    Ponto Focal Prioritário de Deliberação
                  </h2>
                  <p class="text-xs text-zinc-400">
                    Análise com base em atestados, horas extras, turnover e clima para decisão humana imediata.
                  </p>
                </div>
              </div>

              <!-- Lista de Cards Ativos -->
              <div *ngFor="let card of activeCards" class="space-y-4">
                <app-risk-focus-card [card]="card" (resolve)="handleResolveCard($event)"></app-risk-focus-card>
              </div>

              <!-- Estado Vazio (Todos deliberados) -->
              <div
                *ngIf="activeCards.length === 0"
                class="rounded-xl border border-zinc-800 bg-zinc-900/30 p-8 text-center text-zinc-400 space-y-1.5"
              >
                <div class="mx-auto flex h-10 w-10 items-center justify-center rounded-lg bg-zinc-800 text-emerald-400">
                  <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                  </svg>
                </div>
                <h4 class="text-sm font-semibold text-white">Todos os pontos focais foram deliberados</h4>
                <p class="text-xs text-zinc-400">
                  Os planos homologados estão registrados no Inventário do PGR abaixo para ciclo de reavaliação.
                </p>
              </div>
            </div>

            <!-- Tabela Oficial do Inventário do PGR -->
            <app-pgr-inventory-table
              [items]="pgrItems"
              (reassess)="handleReassessItem($event)"
            ></app-pgr-inventory-table>
          </section>

          <!-- ABA 2: Matriz de Áreas & Shield LGPD -->
          <section *ngIf="activeTab === 'areas'" class="space-y-4">
            <div class="rounded-xl border border-zinc-800 bg-zinc-900/30 p-6 space-y-4">
              <div class="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-800/80 pb-4">
                <div>
                  <h2 class="text-sm font-semibold text-white uppercase tracking-wider text-zinc-300">
                    Sinais Históricos por Setor
                  </h2>
                  <p class="text-xs text-zinc-400">
                    Equipes com menos de 5 pessoas têm métricas agregadas bloqueadas por regra estrita de privacidade.
                  </p>
                </div>

                <!-- Seletor de Áreas -->
                <div class="flex flex-wrap items-center gap-1.5">
                  <button
                    *ngFor="let a of availableAreas"
                    type="button"
                    (click)="loadAreaSignals(a.id)"
                    class="rounded-md px-2.5 py-1 text-xs font-mono transition-colors"
                    [ngClass]="selectedAreaId() === a.id ? 'bg-zinc-800 text-white font-semibold border border-zinc-700' : 'bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-zinc-200'"
                  >
                    {{ a.name }} ({{ a.headcount }}p)
                  </button>
                </div>
              </div>

              <!-- Visualização de Sinais da Área -->
              <div *ngIf="currentComparison()" class="pt-1">
                <app-area-signals-view [comparison]="currentComparison()!"></app-area-signals-view>
              </div>
            </div>
          </section>

          <!-- ABA 3: Devolutiva de Escuta ao Colaborador -->
          <section *ngIf="activeTab === 'colaborador'" class="space-y-4">
            <app-feedback-devolutiva-card></app-feedback-devolutiva-card>
          </section>
        </div>

        <!-- Rodapé Discreto -->
        <footer class="border-t border-zinc-900 bg-black py-3 px-8 text-center text-xs text-zinc-500 font-mono">
          vitAI &bull; Governança de Riscos Psicossociais em conformidade com a NR-1 / Portaria MTE nº 1.419/2024.
        </footer>
      </main>

      <!-- Modal de Simulação de Pesquisa Pulso -->
      <app-micro-survey-modal
        *ngIf="isSurveyOpen"
        (closed)="isSurveyOpen = false"
        (submitted)="handleSurveySubmitted()"
      ></app-micro-survey-modal>
    </div>
  `,
})
export class AppComponent implements OnInit {
  private readonly pulsoApi = inject(PulsoApiService);

  activeTab: 'rh' | 'areas' | 'colaborador' = 'rh';
  activeCards: RiskCard[] = [];
  pgrItems: PgrInventoryItem[] = [];
  availableAreas: AreaInfo[] = [];

  selectedAreaId = signal<string>('area_atend');
  currentComparison = signal<AreaHistoryComparison | null>(null);

  isSurveyOpen = false;
  actionSuccessMessage = signal<string | null>(null);
  activeScenario = signal<string>('sc2');

  pitchScenarios = [
    { id: 'sc1', title: '1. Financeiro (Estável)' },
    { id: 'sc2', title: '2. Atendimento (Crítico)' },
    { id: 'sc3', title: '3. Logística (Liderança)' },
    { id: 'sc4', title: '4. Vendas (Compliance)' },
    { id: 'sc5', title: '5. Guardrail LGPD' },
    { id: 'sc6', title: '6. Design (Shield N<5)' },
    { id: 'sc7', title: '7. Ciclo 60d Fechado' },
  ];

  ngOnInit(): void {
    this.loadInitialData();
  }

  loadInitialData(): void {
    this.pulsoApi.listAreas().subscribe((areas) => {
      this.availableAreas = areas;
      this.loadAreaSignals('area_atend');
    });

    this.pulsoApi.listActiveRiskCards().subscribe((cards) => {
      this.activeCards = cards;
    });

    this.pulsoApi.getPgrInventory().subscribe((items) => {
      this.pgrItems = items;
    });
  }

  loadAreaSignals(areaId: string): void {
    this.selectedAreaId.set(areaId);
    this.pulsoApi.getAreaSignals(areaId).subscribe((comp) => {
      this.currentComparison.set(comp);
    });
  }

  handleResolveCard(event: { cardId: string; payload: ResolveRiskCardPayload }): void {
    this.pulsoApi.resolveRiskCard(event.cardId, event.payload).subscribe((newItem) => {
      this.pgrItems = [newItem, ...this.pgrItems.filter((i) => i.itemId !== newItem.itemId)];
      this.activeCards = this.activeCards.filter((c) => c.cardId !== event.cardId);

      const msg =
        event.payload.actionType === 'APROVAR_PGR'
          ? 'Ação aprovada e homologada com sucesso no inventário oficial do PGR.'
          : event.payload.actionType === 'AJUSTAR_ACAO'
          ? 'Plano de ação ajustado e incluído no inventário do PGR com reavaliação programada.'
          : 'Ponto focal descartado com justificativa técnica registrada para auditoria do MTE.';
      this.actionSuccessMessage.set(msg);
      setTimeout(() => this.actionSuccessMessage.set(null), 8000);
    });
  }

  handleReassessItem(itemId: string): void {
    this.pulsoApi.reassessPgrItem(itemId).subscribe((evalResult) => {
      this.pgrItems = this.pgrItems.map((item) => {
        if (item.itemId === itemId) {
          return {
            ...item,
            closureDate: '2026-10-15',
            closureNotes: evalResult.parecer,
          };
        }
        return item;
      });

      this.actionSuccessMessage.set(
        'Caso 7 Concluído com Sucesso: Intervenção eficaz! Risco reavaliado e encerrado no PGR.'
      );
      setTimeout(() => this.actionSuccessMessage.set(null), 8000);
    });
  }

  handleSurveySubmitted(): void {
    this.isSurveyOpen = false;
    this.actionSuccessMessage.set('Pesquisa Pulso submetida pelo colaborador. Sinais recalculados.');
    setTimeout(() => this.actionSuccessMessage.set(null), 6000);
  }

  selectScenario(scId: string): void {
    this.activeScenario.set(scId);

    if (scId === 'sc1') {
      this.activeTab = 'areas';
      this.loadAreaSignals('area_fin');
    } else if (scId === 'sc2') {
      this.activeTab = 'rh';
    } else if (scId === 'sc3') {
      this.activeTab = 'areas';
      this.loadAreaSignals('area_log');
    } else if (scId === 'sc4') {
      this.activeTab = 'areas';
      this.loadAreaSignals('area_vend');
    } else if (scId === 'sc6') {
      this.activeTab = 'areas';
      this.loadAreaSignals('area_des');
    } else if (scId === 'sc7') {
      this.activeTab = 'rh';
      const itemAtend = this.pgrItems.find((i) => i.areaId === 'area_atend');
      if (itemAtend && !itemAtend.closureDate) {
        this.handleReassessItem(itemAtend.itemId);
      }
    }
  }
}
