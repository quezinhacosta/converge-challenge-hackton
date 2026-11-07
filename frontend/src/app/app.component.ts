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
    <div class="min-h-screen bg-[#0A0A0C] text-zinc-100 flex flex-col font-sans selection:bg-[#7C3AED] selection:text-white">
      <!-- Topbar Principal VYTAL.ai (Modern Dark Cyber-Corporate) -->
      <header class="border-b border-zinc-800/80 bg-[#0A0A0C]/90 backdrop-blur-xl sticky top-0 z-40">
        <div class="container mx-auto flex flex-wrap items-center justify-between px-6 py-3.5 gap-4">
          <!-- Logo Oficial VYTAL.ai -->
          <div class="flex items-center gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-[#7C3AED] to-[#5B21B6] text-white shadow-[0_0_20px_rgba(124,58,237,0.4)] border border-violet-500/40">
              <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 4l8 9 8-9"/>
                <path d="M12 13v8"/>
              </svg>
            </div>
            <div>
              <div class="flex items-center gap-1.5">
                <span class="text-xl font-black tracking-tight text-white font-sans">
                  V<span class="text-[#8B5CF6]">Y</span>TAL<span class="text-[#CCFF00]">.ai</span>
                </span>
                <span class="rounded-md bg-zinc-800/90 px-1.5 py-0.5 text-[10px] font-mono text-zinc-400 border border-zinc-700/60">
                  v2.0 NR-1
                </span>
              </div>
              <p class="text-[11px] font-medium text-zinc-400 -mt-0.5">
                Cockpit Executivo de Governança de Riscos Psicossociais
              </p>
            </div>
          </div>

          <!-- Badges de Compliance & Ação Primária -->
          <div class="flex items-center gap-3">
            <span class="hidden md:inline-flex items-center gap-1.5 rounded-full bg-zinc-900 border border-zinc-800 px-3 py-1 text-xs font-mono text-zinc-300">
              NR-1 & Portaria MTE 1.419/2024
            </span>
            <span class="inline-flex items-center gap-2 rounded-full bg-zinc-900 border border-[#CCFF00]/30 px-3 py-1 text-xs font-mono font-bold text-[#CCFF00] shadow-[0_0_12px_rgba(204,255,0,0.15)]">
              <span class="h-2 w-2 rounded-full bg-[#CCFF00] shadow-[0_0_8px_#CCFF00] animate-pulse"></span>
              Engine Ativa (XGBoost + SHAP)
            </span>
            <button
              type="button"
              (click)="isSurveyOpen = true"
              class="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-purple-600 px-4 py-2 text-xs font-bold text-white shadow-[0_0_20px_rgba(124,58,237,0.35)] hover:from-violet-500 hover:to-purple-500 transition-all border border-violet-400/30"
            >
              <svg class="h-4 w-4 text-violet-200" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
              </svg>
              Simular Pesquisa Pulso
            </button>
          </div>
        </div>

        <!-- Barra de Atalhos dos 7 Cenários do Pitch -->
        <div class="border-t border-zinc-800/80 bg-[#121118]/80 py-2.5 px-6">
          <div class="container mx-auto flex items-center gap-2 overflow-x-auto text-xs py-0.5">
            <span class="font-mono font-bold text-[10px] text-zinc-400 shrink-0 uppercase tracking-wider flex items-center gap-1.5">
              <span class="h-1.5 w-1.5 rounded-full bg-[#8B5CF6]"></span>
              Atalhos dos 7 Cenários:
            </span>
            <button
              *ngFor="let sc of pitchScenarios"
              type="button"
              (click)="selectScenario(sc.id)"
              class="shrink-0 rounded-lg px-3 py-1 text-xs font-mono font-semibold transition-all"
              [ngClass]="activeScenario() === sc.id ? 'bg-[#7C3AED] text-white shadow-[0_0_15px_rgba(124,58,237,0.4)] border border-violet-400/40' : 'bg-zinc-900 border border-zinc-800 text-zinc-300 hover:border-zinc-700 hover:text-white'"
            >
              {{ sc.title }}
            </button>
          </div>
        </div>

        <!-- Abas de Navegação -->
        <nav class="container mx-auto flex gap-8 px-6 text-xs sm:text-sm font-semibold border-t border-zinc-800/60">
          <button
            type="button"
            (click)="activeTab = 'rh'"
            class="py-3 border-b-2 transition-all flex items-center gap-2 font-mono"
            [ngClass]="activeTab === 'rh' ? 'border-[#CCFF00] text-[#CCFF00] font-bold shadow-[0_2px_10px_rgba(204,255,0,0.2)]' : 'border-transparent text-zinc-400 hover:text-zinc-200'"
          >
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
            </svg>
            Cockpit de Governança Executiva
          </button>
          <button
            type="button"
            (click)="activeTab = 'areas'"
            class="py-3 border-b-2 transition-all flex items-center gap-2 font-mono"
            [ngClass]="activeTab === 'areas' ? 'border-[#CCFF00] text-[#CCFF00] font-bold shadow-[0_2px_10px_rgba(204,255,0,0.2)]' : 'border-transparent text-zinc-400 hover:text-zinc-200'"
          >
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
            </svg>
            Matriz de Áreas & Shield LGPD
          </button>
          <button
            type="button"
            (click)="activeTab = 'colaborador'"
            class="py-3 border-b-2 transition-all flex items-center gap-2 font-mono"
            [ngClass]="activeTab === 'colaborador' ? 'border-[#CCFF00] text-[#CCFF00] font-bold shadow-[0_2px_10px_rgba(204,255,0,0.2)]' : 'border-transparent text-zinc-400 hover:text-zinc-200'"
          >
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
            </svg>
            Devolutiva ("Você falou, a empresa fez")
          </button>
        </nav>
      </header>

      <!-- Conteúdo Principal -->
      <main class="container mx-auto px-6 py-6 flex-1 space-y-6">
        <!-- Notificação de Ação Executada com Sucesso -->
        <div
          *ngIf="actionSuccessMessage()"
          class="rounded-2xl border border-emerald-500/40 bg-emerald-950/40 p-4 text-xs font-mono font-bold text-[#CCFF00] flex items-center justify-between shadow-[0_0_20px_rgba(204,255,0,0.2)] animate-fadeIn backdrop-blur-md"
        >
          <div class="flex items-center gap-2.5">
            <svg class="h-5 w-5 text-[#CCFF00]" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
            </svg>
            <span>{{ actionSuccessMessage() }}</span>
          </div>
          <button type="button" (click)="actionSuccessMessage.set(null)" class="text-zinc-400 hover:text-white text-base">
            &times;
          </button>
        </div>

        <!-- Grid de KPIs Executivos (4 Cards Glassmorphism) -->
        <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <!-- KPI 1 -->
          <div class="rounded-2xl border border-zinc-800 bg-[#121118]/80 p-4.5 backdrop-blur-md shadow-glass">
            <div class="flex items-center justify-between">
              <span class="text-xs font-mono font-medium text-zinc-400">Vidas Monitoradas</span>
              <span class="h-2 w-2 rounded-xs bg-[#CCFF00] shadow-[0_0_8px_#CCFF00]"></span>
            </div>
            <div class="mt-2 flex items-baseline gap-2">
              <span class="text-3xl font-extrabold font-mono text-white">154</span>
              <span class="text-xs font-mono text-zinc-500">colaboradores</span>
            </div>
            <p class="text-[11px] text-zinc-400 mt-1">
              Ativos na folha e ponto operacional
            </p>
          </div>

          <!-- KPI 2 -->
          <div class="rounded-2xl border border-zinc-800 bg-[#121118]/80 p-4.5 backdrop-blur-md shadow-glass">
            <div class="flex items-center justify-between">
              <span class="text-xs font-mono font-medium text-zinc-400">Áreas Mapeadas</span>
              <span class="h-2 w-2 rounded-full bg-[#8B5CF6] shadow-[0_0_8px_#8B5CF6]"></span>
            </div>
            <div class="mt-2 flex items-baseline gap-2">
              <span class="text-3xl font-extrabold font-mono text-white">7</span>
              <span class="text-xs font-mono text-[#CCFF00]">6 ativas &bull; 1 shield</span>
            </div>
            <p class="text-[11px] text-zinc-400 mt-1">
              Design (3p) protegido por quórum LGPD
            </p>
          </div>

          <!-- KPI 3 -->
          <div class="rounded-2xl border border-zinc-800 bg-[#121118]/80 p-4.5 backdrop-blur-md shadow-glass">
            <div class="flex items-center justify-between">
              <span class="text-xs font-mono font-medium text-zinc-400">Pontos Focais de Risco</span>
              <span class="h-2 w-2 rounded-full bg-rose-500 shadow-[0_0_8px_#F43F5E] animate-pulse"></span>
            </div>
            <div class="mt-2 flex items-baseline gap-2">
              <span class="text-3xl font-extrabold font-mono text-rose-400">{{ activeCards.length }}</span>
              <span class="text-xs font-mono text-zinc-400">pendentes</span>
            </div>
            <p class="text-[11px] text-zinc-400 mt-1">
              Atendimento (Crítico) e Logística
            </p>
          </div>

          <!-- KPI 4 -->
          <div class="rounded-2xl border border-zinc-800 bg-[#121118]/80 p-4.5 backdrop-blur-md shadow-glass">
            <div class="flex items-center justify-between">
              <span class="text-xs font-mono font-medium text-zinc-400">Conformidade NR-1 / PGR</span>
              <span class="h-2 w-2 rounded-full bg-[#CCFF00] shadow-[0_0_8px_#CCFF00]"></span>
            </div>
            <div class="mt-2 flex items-baseline gap-2">
              <span class="text-3xl font-extrabold font-mono text-[#CCFF00]">94.2%</span>
              <span class="text-xs font-mono text-emerald-400">auditável</span>
            </div>
            <p class="text-[11px] text-zinc-400 mt-1">
              PGR atualizado conforme MTE 1.419
            </p>
          </div>
        </section>

        <!-- ABA 1: Cockpit do RH (Zero Chatbot - Ponto Focal e Tabela PGR) -->
        <section *ngIf="activeTab === 'rh'" class="space-y-6">
          <!-- Ponto Focal Principal -->
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <div>
                <h2 class="text-lg font-bold text-white flex items-center gap-2">
                  <span class="h-2 w-2 rounded-xs bg-[#CCFF00] shadow-[0_0_8px_#CCFF00]"></span>
                  Ponto Focal Prioritário de Deliberação
                  <span class="rounded-full bg-rose-950/60 border border-rose-800/60 px-2.5 py-0.5 text-xs font-mono font-bold text-rose-400">
                    {{ activeCards.length }} Requer Atenção
                  </span>
                </h2>
                <p class="text-xs text-zinc-400">
                  O motor XGBoost cruza atestados, horas extras, turnover e clima para gerar o plano de ação pronto para sua decisão.
                </p>
              </div>
            </div>

            <!-- Lista de Cards Ativos -->
            <div *ngFor="let card of activeCards" class="space-y-4">
              <app-risk-focus-card [card]="card" (resolve)="handleResolveCard($event)"></app-risk-focus-card>
            </div>

            <div
              *ngIf="activeCards.length === 0"
              class="rounded-2xl border border-zinc-800 bg-[#121118]/80 p-8 text-center text-zinc-400 space-y-2 shadow-glass backdrop-blur-md"
            >
              <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-zinc-900 border border-[#CCFF00]/40 text-[#CCFF00] shadow-[0_0_20px_rgba(204,255,0,0.25)]">
                <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
                </svg>
              </div>
              <h4 class="text-base font-bold text-white">Todos os pontos focais foram deliberados</h4>
              <p class="text-xs text-zinc-400">
                Os planos aprovados constam no Inventário do PGR abaixo para acompanhamento dos ciclos de 60 dias.
              </p>
            </div>
          </div>

          <!-- Tabela do Inventário do PGR (NR-1 Oficial) -->
          <app-pgr-inventory-table
            [items]="pgrItems"
            (reassess)="handleReassessItem($event)"
          ></app-pgr-inventory-table>
        </section>

        <!-- ABA 2: Visão de Áreas & Anonimização (Shield LGPD N < 5) -->
        <section *ngIf="activeTab === 'areas'" class="space-y-6">
          <div class="rounded-2xl border border-zinc-800 bg-[#121118]/90 p-6 backdrop-blur-md shadow-glass space-y-4">
            <div class="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-800/80 pb-4">
              <div>
                <h2 class="text-lg font-bold text-white flex items-center gap-2">
                  <span class="h-2 w-2 rounded-xs bg-[#CCFF00] shadow-[0_0_8px_#CCFF00]"></span>
                  Matriz de Áreas & Shield LGPD
                </h2>
                <p class="text-xs text-zinc-400">
                  Validação do guardrail ético: equipes com menos de 5 colaboradores têm seus dados ocultados automaticamente.
                </p>
              </div>

              <!-- Seletor de Áreas -->
              <div class="flex flex-wrap items-center gap-2">
                <button
                  *ngFor="let a of availableAreas"
                  type="button"
                  (click)="loadAreaSignals(a.id)"
                  class="rounded-xl px-3 py-1.5 text-xs font-mono font-semibold transition-all"
                  [ngClass]="selectedAreaId() === a.id ? 'bg-[#7C3AED] text-white shadow-[0_0_15px_rgba(124,58,237,0.4)] border border-violet-400/40' : 'bg-zinc-900 border border-zinc-800 text-zinc-300 hover:border-zinc-700 hover:text-white'"
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
        <section *ngIf="activeTab === 'colaborador'" class="space-y-6">
          <app-feedback-devolutiva-card></app-feedback-devolutiva-card>
        </section>
      </main>

      <!-- Modal de Simulação da Pesquisa Pulso -->
      <app-micro-survey-modal
        *ngIf="isSurveyOpen"
        (closed)="isSurveyOpen = false"
        (submitted)="handleSurveySubmitted()"
      ></app-micro-survey-modal>

      <!-- Rodapé Minimalista VYTAL.ai -->
      <footer class="border-t border-zinc-900 bg-[#0A0A0C] py-4 px-6 text-center text-xs text-zinc-500 font-mono">
        VYTAL.ai &bull; Governança de Riscos Psicossociais em conformidade com a NR-1 / Portaria MTE nº 1.419/2024.
      </footer>
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
