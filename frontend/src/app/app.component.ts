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
    <div class="min-h-screen bg-[#070709] text-zinc-100 flex flex-row font-sans antialiased relative overflow-hidden selection:bg-violet-600 selection:text-white">
      <!-- Elementos Visuais Dinâmicos de Fundo (Glows Flutuantes em Movimento) -->
      <div class="fixed -top-24 left-48 w-[450px] h-[450px] bg-violet-600/10 rounded-full blur-[120px] pointer-events-none animate-float"></div>
      <div class="fixed top-1/2 right-12 w-[500px] h-[500px] bg-teal-500/10 rounded-full blur-[140px] pointer-events-none animate-float-reverse"></div>
      <div class="fixed bottom-0 left-1/3 w-[400px] h-[400px] bg-indigo-600/10 rounded-full blur-[130px] pointer-events-none animate-pulse-glow"></div>

      <!-- Barra Lateral Esquerda (Navegação Vertical Executiva) -->
      <aside class="w-72 shrink-0 bg-[#0a0a0e]/95 backdrop-blur-xl border-r border-zinc-800/80 flex flex-col justify-between h-screen sticky top-0 z-30 select-none shadow-2xl">
        <div class="flex flex-col h-full overflow-y-auto">
          <!-- Cabeçalho e Marca vitAI -->
          <div class="p-6 border-b border-zinc-800/70">
            <div class="flex items-center gap-3">
              <div class="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-tr from-violet-600 via-indigo-600 to-teal-400 text-white font-extrabold text-lg shadow-lg shadow-violet-900/40 border border-violet-400/30 animate-gradient-flow">
                V
              </div>
              <div>
                <div class="flex items-center gap-2">
                  <span class="text-xl font-black tracking-tight text-white">
                    vit<span class="bg-gradient-to-r from-violet-400 via-indigo-300 to-teal-300 bg-clip-text text-transparent">AI</span>
                  </span>
                  <span class="rounded-md bg-zinc-800/90 px-2 py-0.5 text-xs font-mono font-bold text-zinc-300 border border-zinc-700/80">
                    NR-1
                  </span>
                </div>
                <p class="text-xs text-zinc-400 font-medium mt-0.5">Governança Psicossocial</p>
              </div>
            </div>

            <!-- Status do Motor com Radar Pulsante -->
            <div class="mt-4 flex items-center justify-between rounded-xl bg-zinc-900/90 border border-zinc-800 px-3.5 py-2 text-xs text-zinc-200 font-mono shadow-inner">
              <div class="flex items-center gap-2.5">
                <span class="relative flex h-2.5 w-2.5">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                </span>
                <span class="font-semibold text-zinc-200">Motor Ativo (XGBoost)</span>
              </div>
              <span class="text-[10px] text-zinc-400 font-bold">2.0</span>
            </div>
          </div>

          <!-- Módulos de Navegação -->
          <nav class="p-4 space-y-1.5">
            <div class="px-2 pb-1.5 text-xs font-mono font-bold uppercase tracking-wider text-zinc-400">
              Módulos do Sistema
            </div>

            <button
              type="button"
              (click)="activeTab = 'rh'"
              class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all text-left group"
              [ngClass]="activeTab === 'rh' ? 'bg-gradient-to-r from-violet-900/40 to-zinc-900 text-white font-bold border-l-4 border-violet-500 shadow-md' : 'text-zinc-400 hover:text-white hover:bg-zinc-900/70'"
            >
              <svg class="h-5 w-5 shrink-0 transition-transform group-hover:scale-110" [ngClass]="activeTab === 'rh' ? 'text-violet-400' : 'text-zinc-400'" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
              </svg>
              <span>Cockpit Executivo</span>
            </button>

            <button
              type="button"
              (click)="activeTab = 'areas'"
              class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all text-left group"
              [ngClass]="activeTab === 'areas' ? 'bg-gradient-to-r from-violet-900/40 to-zinc-900 text-white font-bold border-l-4 border-violet-500 shadow-md' : 'text-zinc-400 hover:text-white hover:bg-zinc-900/70'"
            >
              <svg class="h-5 w-5 shrink-0 transition-transform group-hover:scale-110" [ngClass]="activeTab === 'areas' ? 'text-violet-400' : 'text-zinc-400'" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
              </svg>
              <span>Matriz & Shield LGPD</span>
            </button>

            <button
              type="button"
              (click)="activeTab = 'colaborador'"
              class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all text-left group"
              [ngClass]="activeTab === 'colaborador' ? 'bg-gradient-to-r from-violet-900/40 to-zinc-900 text-white font-bold border-l-4 border-violet-500 shadow-md' : 'text-zinc-400 hover:text-white hover:bg-zinc-900/70'"
            >
              <svg class="h-5 w-5 shrink-0 transition-transform group-hover:scale-110" [ngClass]="activeTab === 'colaborador' ? 'text-violet-400' : 'text-zinc-400'" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
              </svg>
              <span>Devolutiva ao Time</span>
            </button>
          </nav>

          <!-- Cenários de Teste / Pitch (Lista Visual com Efeito Gradiente) -->
          <div class="p-4 border-t border-zinc-800/80">
            <div class="px-2 pb-2.5 text-xs font-mono font-bold uppercase tracking-wider text-zinc-400 flex items-center justify-between">
              <span>Cenários de Teste</span>
              <span class="text-[10px] text-zinc-500">7 fluxos</span>
            </div>
            <div class="space-y-1">
              <button
                *ngFor="let sc of pitchScenarios"
                type="button"
                (click)="selectScenario(sc.id)"
                class="w-full text-left px-3 py-2 rounded-lg text-xs font-mono transition-all flex items-center justify-between group"
                [ngClass]="activeScenario() === sc.id ? 'bg-gradient-to-r from-zinc-800 to-zinc-800/60 text-white font-bold border border-zinc-600 shadow-sm' : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/60'"
              >
                <span>{{ sc.title }}</span>
                <span *ngIf="activeScenario() === sc.id" class="h-1.5 w-1.5 rounded-full bg-violet-400"></span>
              </button>
            </div>
          </div>

          <!-- Ação Inferior da Barra Lateral -->
          <div class="mt-auto p-4 border-t border-zinc-800/80 space-y-2.5">
            <button
              type="button"
              (click)="isSurveyOpen = true"
              class="w-full inline-flex items-center justify-center gap-2.5 rounded-xl bg-gradient-to-r from-violet-600 via-indigo-600 to-teal-500 hover:from-violet-500 hover:to-teal-400 text-white font-bold px-4 py-2.5 text-xs shadow-lg shadow-violet-950/60 transition-all hover:scale-[1.02] active:scale-95"
            >
              <svg class="h-4 w-4 text-violet-100" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
              </svg>
              Simular Pesquisa Pulso
            </button>
            <p class="text-[11px] text-zinc-400 font-mono text-center">
              Portaria MTE nº 1.419/2024
            </p>
          </div>
        </div>
      </aside>

      <!-- Conteúdo Principal à Direita -->
      <main class="flex-1 bg-transparent min-h-screen overflow-y-auto flex flex-col relative z-10">
        <!-- Barra de Topo da Área de Conteúdo -->
        <header class="border-b border-zinc-800/70 bg-[#0a0a0e]/80 backdrop-blur-xl px-10 py-5 flex items-center justify-between sticky top-0 z-20 shadow-md">
          <div>
            <h1 class="text-xl font-black text-white tracking-tight flex items-center gap-2">
              <span class="bg-gradient-to-r from-white via-zinc-200 to-zinc-400 bg-clip-text text-transparent">
                {{ activeTab === 'rh' ? 'Cockpit de Governança Executiva' : (activeTab === 'areas' ? 'Matriz de Áreas & Shield LGPD' : 'Devolutiva de Escuta ao Time') }}
              </span>
            </h1>
            <p class="text-sm text-zinc-300 font-medium mt-0.5">
              Auditoria em tempo real e mitigação contínua de fatores psicossociais da NR-1.
            </p>
          </div>

          <div class="flex items-center gap-3">
            <span class="inline-flex items-center gap-2 rounded-lg bg-zinc-900/90 border border-zinc-700/80 px-3.5 py-1.5 text-xs font-mono font-bold text-zinc-200 shadow-sm">
              <span class="h-2 w-2 rounded-full bg-teal-400 animate-pulse"></span>
              Portaria MTE 1.419/2024
            </span>
          </div>
        </header>

        <!-- Corpo da Página -->
        <div class="p-10 space-y-8 max-w-7xl w-full mx-auto flex-1">
          <!-- Mensagem de Sucesso de Ação com Efeito Gradiente -->
          <div
            *ngIf="actionSuccessMessage()"
            class="rounded-xl border border-emerald-500/40 bg-gradient-to-r from-emerald-950/60 via-zinc-900 to-emerald-950/40 p-4 text-sm font-mono text-emerald-300 flex items-center justify-between shadow-lg shadow-emerald-950/50 backdrop-blur-md"
          >
            <div class="flex items-center gap-3">
              <span class="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-500/20 text-emerald-400 shrink-0">
                <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                </svg>
              </span>
              <span class="font-bold text-emerald-200">{{ actionSuccessMessage() }}</span>
            </div>
            <button type="button" (click)="actionSuccessMessage.set(null)" class="text-zinc-400 hover:text-white text-lg">
              &times;
            </button>
          </div>

          <!-- Indicadores Executivos Principais (4 KPIs de Alto Impacto Visual) -->
          <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            <!-- KPI 1 -->
            <div class="group relative rounded-2xl border border-zinc-800/80 bg-zinc-900/60 p-5 backdrop-blur-md shadow-xl hover:-translate-y-1 hover:border-zinc-700 transition-all duration-300">
              <div class="absolute inset-x-0 top-0 h-1 rounded-t-2xl bg-gradient-to-r from-violet-500 to-indigo-500 opacity-60 group-hover:opacity-100 transition-opacity"></div>
              <div class="flex items-center justify-between text-xs font-semibold text-zinc-300">
                <span class="uppercase tracking-wider">Vidas Monitoradas</span>
                <span class="rounded bg-zinc-800 px-2 py-0.5 text-[10px] font-mono text-zinc-400">Ativos</span>
              </div>
              <div class="mt-3 flex items-baseline gap-2">
                <span class="text-4xl font-black font-mono text-white tracking-tight">154</span>
                <span class="text-sm font-semibold text-zinc-300">colaboradores</span>
              </div>
              <p class="text-xs text-zinc-300 font-medium mt-1.5">100% da folha e ponto operacional</p>
            </div>

            <!-- KPI 2 -->
            <div class="group relative rounded-2xl border border-zinc-800/80 bg-zinc-900/60 p-5 backdrop-blur-md shadow-xl hover:-translate-y-1 hover:border-zinc-700 transition-all duration-300">
              <div class="absolute inset-x-0 top-0 h-1 rounded-t-2xl bg-gradient-to-r from-indigo-500 to-teal-500 opacity-60 group-hover:opacity-100 transition-opacity"></div>
              <div class="flex items-center justify-between text-xs font-semibold text-zinc-300">
                <span class="uppercase tracking-wider">Áreas Mapeadas</span>
                <span class="rounded bg-zinc-800 px-2 py-0.5 text-[10px] font-mono text-teal-400">Quórum</span>
              </div>
              <div class="mt-3 flex items-baseline gap-2">
                <span class="text-4xl font-black font-mono text-white tracking-tight">7</span>
                <span class="text-sm font-semibold text-zinc-300">setores (1 protegido)</span>
              </div>
              <p class="text-xs text-zinc-300 font-medium mt-1.5">Design (3p) resguardado por sigilo</p>
            </div>

            <!-- KPI 3 -->
            <div class="group relative rounded-2xl border border-zinc-800/80 bg-zinc-900/60 p-5 backdrop-blur-md shadow-xl hover:-translate-y-1 hover:border-zinc-700 transition-all duration-300">
              <div class="absolute inset-x-0 top-0 h-1 rounded-t-2xl bg-gradient-to-r from-rose-500 to-amber-500 opacity-60 group-hover:opacity-100 transition-opacity"></div>
              <div class="flex items-center justify-between text-xs font-semibold text-zinc-300">
                <span class="uppercase tracking-wider">Pontos Focais de Risco</span>
                <span class="rounded bg-rose-950/60 border border-rose-800/60 px-2 py-0.5 text-[10px] font-mono font-bold text-rose-300 animate-pulse">Atenção</span>
              </div>
              <div class="mt-3 flex items-baseline gap-2">
                <span class="text-4xl font-black font-mono tracking-tight" [ngClass]="activeCards.length > 0 ? 'text-rose-400' : 'text-white'">
                  {{ activeCards.length }}
                </span>
                <span class="text-sm font-semibold text-zinc-300">pendências</span>
              </div>
              <p class="text-xs text-zinc-300 font-medium mt-1.5">Atendimento ao Cliente e Logística</p>
            </div>

            <!-- KPI 4 -->
            <div class="group relative rounded-2xl border border-zinc-800/80 bg-zinc-900/60 p-5 backdrop-blur-md shadow-xl hover:-translate-y-1 hover:border-zinc-700 transition-all duration-300">
              <div class="absolute inset-x-0 top-0 h-1 rounded-t-2xl bg-gradient-to-r from-emerald-500 to-teal-400 opacity-60 group-hover:opacity-100 transition-opacity"></div>
              <div class="flex items-center justify-between text-xs font-semibold text-zinc-300">
                <span class="uppercase tracking-wider">Conformidade PGR</span>
                <span class="rounded bg-emerald-950/60 border border-emerald-800/60 px-2 py-0.5 text-[10px] font-mono font-bold text-emerald-300">Auditável</span>
              </div>
              <div class="mt-3 flex items-baseline gap-2">
                <span class="text-4xl font-black font-mono text-emerald-400 tracking-tight">94.2%</span>
                <span class="text-sm font-semibold text-zinc-300">cobertura</span>
              </div>
              <p class="text-xs text-zinc-300 font-medium mt-1.5">Planos alinhados à Portaria MTE</p>
            </div>
          </section>

          <!-- ABA 1: Cockpit Executivo (Ponto Focal + Tabela PGR) -->
          <section *ngIf="activeTab === 'rh'" class="space-y-8">
            <!-- Ponto Focal Principal -->
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <div>
                  <h2 class="text-lg font-black text-white uppercase tracking-wider flex items-center gap-2">
                    <span class="h-2.5 w-2.5 rounded-full bg-violet-400 animate-pulse"></span>
                    Ponto Focal Prioritário de Deliberação
                  </h2>
                  <p class="text-sm text-zinc-300 font-medium mt-0.5">
                    Cruzamento analítico de atestados, horas extras, turnover e clima pronto para decisão humana.
                  </p>
                </div>
              </div>

              <!-- Lista de Cards Ativos -->
              <div *ngFor="let card of activeCards" class="space-y-5">
                <app-risk-focus-card [card]="card" (resolve)="handleResolveCard($event)"></app-risk-focus-card>
              </div>

              <!-- Estado Vazio (Todos deliberados) -->
              <div
                *ngIf="activeCards.length === 0"
                class="rounded-2xl border border-zinc-800/80 bg-zinc-900/50 p-10 text-center text-zinc-300 space-y-2 shadow-xl backdrop-blur-md"
              >
                <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-950/60 border border-emerald-800/60 text-emerald-400">
                  <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                  </svg>
                </div>
                <h4 class="text-base font-bold text-white">Todos os pontos focais foram deliberados</h4>
                <p class="text-sm text-zinc-300">
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
          <section *ngIf="activeTab === 'areas'" class="space-y-5">
            <div class="rounded-2xl border border-zinc-800/80 bg-zinc-900/50 p-8 backdrop-blur-md shadow-xl space-y-5">
              <div class="flex flex-wrap items-center justify-between gap-4 border-b border-zinc-800/80 pb-5">
                <div>
                  <h2 class="text-lg font-black text-white uppercase tracking-wider flex items-center gap-2">
                    <span class="h-2.5 w-2.5 rounded-full bg-teal-400"></span>
                    Sinais Históricos por Setor
                  </h2>
                  <p class="text-sm text-zinc-300 font-medium mt-0.5">
                    Equipes com menos de 5 pessoas têm métricas agregadas bloqueadas por regra legal de anonimização.
                  </p>
                </div>

                <!-- Seletor de Áreas -->
                <div class="flex flex-wrap items-center gap-2">
                  <button
                    *ngFor="let a of availableAreas"
                    type="button"
                    (click)="loadAreaSignals(a.id)"
                    class="rounded-xl px-3.5 py-2 text-xs font-mono font-bold transition-all shadow-sm"
                    [ngClass]="selectedAreaId() === a.id ? 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white shadow-md shadow-violet-900/40 border border-violet-400/40' : 'bg-zinc-900 border border-zinc-800 text-zinc-300 hover:border-zinc-700 hover:text-white'"
                  >
                    {{ a.name }} ({{ a.headcount }}p)
                  </button>
                </div>
              </div>

              <!-- Visualização de Sinais da Área -->
              <div *ngIf="currentComparison()" class="pt-2">
                <app-area-signals-view [comparison]="currentComparison()!"></app-area-signals-view>
              </div>
            </div>
          </section>

          <!-- ABA 3: Devolutiva de Escuta ao Colaborador -->
          <section *ngIf="activeTab === 'colaborador'" class="space-y-5">
            <app-feedback-devolutiva-card></app-feedback-devolutiva-card>
          </section>
        </div>

        <!-- Rodapé Discreto -->
        <footer class="border-t border-zinc-800/60 bg-[#08080b]/90 py-4 px-10 text-center text-xs text-zinc-400 font-mono">
          vitAI &bull; Governança de Riscos Psicossociais em estrita conformidade com a NR-1 / Portaria MTE nº 1.419/2024.
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
