import { Component, Input, Output, EventEmitter, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RiskCard, ResolveRiskCardPayload } from '../../../../core/models/risk-card.model';

@Component({
  selector: 'app-risk-focus-card',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <article
      *ngIf="card"
      class="group relative overflow-hidden rounded-2xl transition-all duration-300 backdrop-blur-md"
      [ngClass]="{
        'border border-violet-500/40 bg-[#121118]/90 shadow-[0_0_35px_rgba(124,58,237,0.15)]': card.riskLevel === 'VERMELHO',
        'border border-amber-500/30 bg-[#121118]/85 shadow-[0_0_25px_rgba(245,158,11,0.10)]': card.riskLevel === 'AMARELO',
        'border border-zinc-800 bg-[#121118]/80': card.riskLevel === 'VERDE',
        'opacity-60 bg-zinc-950/90 border-zinc-800/60': isApproved()
      }"
    >
      <!-- Faixa lateral de status com brilho neon -->
      <div
        class="absolute left-0 top-0 bottom-0 w-1.5"
        [ngClass]="{
          'bg-gradient-to-b from-rose-500 to-violet-600 shadow-[0_0_12px_#F43F5E]': card.riskLevel === 'VERMELHO',
          'bg-gradient-to-b from-amber-400 to-amber-600 shadow-[0_0_10px_#F59E0B]': card.riskLevel === 'AMARELO',
          'bg-[#CCFF00] shadow-[0_0_10px_#CCFF00]': card.riskLevel === 'VERDE'
        }"
      ></div>

      <div class="p-6 pl-8 space-y-5">
        <!-- Header: Severidade, Área, Headcount, Score XGBoost e Provedor de IA -->
        <header class="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-800/80 pb-4">
          <div class="flex flex-wrap items-center gap-2.5">
            <!-- Pílula de Severidade com Dot Pulsante Neon -->
            <span
              class="inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-bold uppercase tracking-wider"
              [ngClass]="{
                'bg-rose-950/60 text-rose-400 border border-rose-800/50 shadow-[0_0_15px_rgba(244,63,94,0.2)]': card.riskLevel === 'VERMELHO',
                'bg-amber-950/50 text-amber-300 border border-amber-800/40': card.riskLevel === 'AMARELO',
                'bg-emerald-950/50 text-[#CCFF00] border border-emerald-800/40': card.riskLevel === 'VERDE'
              }"
            >
              <span
                class="h-2 w-2 rounded-full"
                [ngClass]="{
                  'bg-rose-500 animate-pulse shadow-[0_0_8px_#F43F5E]': card.riskLevel === 'VERMELHO' && !isApproved(),
                  'bg-amber-400': card.riskLevel === 'AMARELO' && !isApproved(),
                  'bg-[#CCFF00] shadow-[0_0_8px_#CCFF00]': card.riskLevel === 'VERDE' || isApproved()
                }"
              ></span>
              Risco {{ card.riskLevel === 'VERMELHO' ? 'Crítico (Alto)' : (card.riskLevel === 'AMARELO' ? 'Moderado (Médio)' : 'Estável') }}
            </span>

            <!-- Score Matemático do XGBoost -->
            <span
              *ngIf="card.riskScore"
              class="inline-flex items-center gap-1.5 rounded-lg bg-zinc-900/90 px-2.5 py-1 text-xs font-mono font-bold text-zinc-100 border border-zinc-800"
            >
              <span class="h-1.5 w-1.5 rounded-full bg-[#8B5CF6]"></span>
              Score ML: <span class="text-[#CCFF00]">{{ card.riskScore }}</span> / 100
            </span>

            <!-- Badge Fator de Risco da NR-1 -->
            <span class="inline-flex items-center gap-1.5 rounded-lg bg-violet-950/40 px-2.5 py-1 text-xs font-medium text-violet-300 border border-violet-800/40">
              <svg class="h-3.5 w-3.5 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
              Fator NR-1: {{ formatFator(card.fatorRiscoProvavel) }}
            </span>
          </div>

          <div class="flex flex-wrap items-center gap-2 text-xs text-zinc-400">
            <!-- Indicador do Provedor de IA e Resiliência -->
            <span
              class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[11px] font-mono border"
              [ngClass]="card.aiFallbackTriggered ? 'bg-amber-950/40 text-amber-300 border-amber-800/50' : 'bg-zinc-900/90 text-zinc-300 border-zinc-800'"
              [title]="card.aiFallbackTriggered ? 'Plano de contingência ativado: IA substituída automaticamente' : 'Execução nominal'"
            >
              <svg class="h-3 w-3 text-[#CCFF00]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
              {{ card.aiProviderUsed || 'xgboost + gemini-1.5-pro' }}
              <span *ngIf="card.aiFallbackTriggered" class="font-bold text-amber-400">(Failover Ativo)</span>
            </span>

            <span
              class="rounded-full px-2.5 py-0.5 font-semibold text-xs border"
              [ngClass]="{
                'bg-zinc-900 text-zinc-400 border-zinc-800': card.status === 'ABERTO' && !isApproved(),
                'bg-[#CCFF00]/10 text-[#CCFF00] border-[#CCFF00]/30 shadow-[0_0_10px_rgba(204,255,0,0.15)]': isApproved()
              }"
            >
              {{ isApproved() ? 'HOMOLOGADO NO PGR' : 'AGUARDANDO DELIBERAÇÃO' }}
            </span>
          </div>
        </header>

        <!-- Título e Subtítulo da Área -->
        <div>
          <div class="flex items-center gap-2">
            <span class="h-2 w-2 rounded-xs bg-[#CCFF00] shadow-[0_0_8px_#CCFF00]"></span>
            <h3 class="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              Área: {{ card.areaName }}
              <span class="text-xs font-mono font-normal text-zinc-400 border border-zinc-800 bg-zinc-900/80 px-2 py-0.5 rounded-md">
                {{ card.areaHeadcount }} colaboradores
              </span>
            </h3>
          </div>
          <p class="text-xs text-zinc-400 mt-1">
            Conformidade Trabalhista: Portaria MTE nº 1.419/2024 e NR-1 (Capítulo GRO e PGR)
          </p>
        </div>

        <!-- Bloco 1: Evidências Objetivas Consolidadas (Deltas vs Histórico) -->
        <section class="rounded-xl border border-zinc-800/80 bg-zinc-950/60 p-4">
          <h4 class="text-xs font-bold uppercase tracking-wider text-zinc-400 mb-3 flex items-center gap-2">
            <svg class="h-4 w-4 text-[#8B5CF6]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
            </svg>
            Evidências Quantitativas Consolidadas (Deltas vs Histórico do Time)
          </h4>

          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div class="rounded-xl bg-zinc-900/80 p-3.5 border border-zinc-800/80">
              <span class="block text-[11px] font-medium text-zinc-400">Dias de Atestado</span>
              <div class="mt-1 flex items-baseline gap-1.5">
                <span class="text-2xl font-bold font-mono text-rose-400">+45%</span>
                <span class="text-[10px] text-zinc-500 font-mono">trimestre</span>
              </div>
            </div>

            <div class="rounded-xl bg-zinc-900/80 p-3.5 border border-zinc-800/80">
              <span class="block text-[11px] font-medium text-zinc-400">Horas Extras</span>
              <div class="mt-1 flex items-baseline gap-1.5">
                <span class="text-2xl font-bold font-mono text-rose-400">+60%</span>
                <span class="text-[10px] text-zinc-500 font-mono">sobrecarga</span>
              </div>
            </div>

            <div class="rounded-xl bg-zinc-900/80 p-3.5 border border-zinc-800/80">
              <span class="block text-[11px] font-medium text-zinc-400">Saídas Voluntárias</span>
              <div class="mt-1 flex items-baseline gap-1.5">
                <span class="text-2xl font-bold font-mono text-amber-400">4</span>
                <span class="text-[10px] text-zinc-500 font-mono">média: 1</span>
              </div>
            </div>

            <div class="rounded-xl bg-zinc-900/80 p-3.5 border border-zinc-800/80">
              <span class="block text-[11px] font-medium text-zinc-400">Nota Pesquisa Pulso</span>
              <div class="mt-1 flex items-baseline gap-1.5">
                <span class="text-2xl font-bold font-mono text-rose-400">2.4</span>
                <span class="text-[10px] text-zinc-500 line-through font-mono">3.9</span>
              </div>
            </div>
          </div>

          <p class="mt-3.5 text-xs text-zinc-300 leading-relaxed border-t border-zinc-800/60 pt-2.5">
            <span class="font-bold text-white">Síntese dos Fatos:</span>
            {{ card.oQueMudouUltimosMeses }}
          </p>
        </section>

        <!-- Bloco 2: Explicabilidade Legal e Decomposição SHAP (O "Cérebro Matemático" XGBoost) -->
        <section
          *ngIf="card.shapBreakdown && card.shapBreakdown.length > 0"
          class="rounded-xl border border-violet-800/40 bg-violet-950/20 p-4 space-y-3"
        >
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div class="flex items-center gap-2">
              <span class="flex h-6 w-6 items-center justify-center rounded-lg bg-[#7C3AED] text-white shadow-[0_0_12px_rgba(124,58,237,0.4)]">
                <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                </svg>
              </span>
              <h4 class="text-xs font-bold uppercase tracking-wider text-violet-200">
                Auditoria de Explicabilidade Legal (SHAP / NR-1)
              </h4>
            </div>
            <span class="rounded bg-violet-900/50 px-2 py-0.5 text-[10px] font-mono font-bold text-violet-300 border border-violet-700/50">
              Modelo: XGBoost v1.2 &bull; Sem Caixa-Preta
            </span>
          </div>

          <p class="text-[11px] text-zinc-400">
            Decomposição de Shapley para comprovação matemática de nexo causal sem alucinações de LLM:
          </p>

          <!-- Barras de Decomposição das Contribuições de Shapley -->
          <div class="space-y-2.5 pt-1">
            <div *ngFor="let item of card.shapBreakdown" class="space-y-1">
              <div class="flex items-center justify-between text-xs">
                <span class="font-medium text-zinc-200 flex items-center gap-2">
                  <span class="h-1.5 w-1.5 rounded-full bg-[#8B5CF6] shadow-[0_0_6px_#8B5CF6]"></span>
                  {{ item.display_name }}
                  <span class="text-[10px] font-mono text-zinc-500">({{ item.observed_value }})</span>
                </span>
                <span class="font-bold font-mono text-[#CCFF00]">
                  {{ item.contribution_pct }}% do risco
                </span>
              </div>
              <div class="h-2 w-full overflow-hidden rounded-full bg-zinc-800">
                <div
                  class="h-full rounded-full transition-all duration-700"
                  [ngClass]="item.contribution_pct > 30 ? 'bg-gradient-to-r from-violet-600 to-rose-500' : (item.contribution_pct > 20 ? 'bg-gradient-to-r from-violet-600 to-indigo-500' : 'bg-gradient-to-r from-amber-500 to-yellow-400')"
                  [style.width.%]="item.contribution_pct"
                ></div>
              </div>
            </div>
          </div>
        </section>

        <!-- Bloco 3: Hipótese de Contexto (Motor de IA / Correlação Temporal) -->
        <section class="rounded-xl border border-violet-800/40 bg-gradient-to-r from-violet-950/40 via-[#181822] to-violet-950/20 p-4">
          <div class="flex items-start gap-3">
            <div class="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-[#7C3AED] text-white shadow-[0_0_15px_rgba(124,58,237,0.4)]">
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
            </div>
            <div class="space-y-1">
              <div class="flex items-center gap-2">
                <h5 class="text-xs font-bold uppercase tracking-wider text-violet-200">
                  Hipótese de Contexto Organizacional (Digital Worker VYTAL.ai)
                </h5>
                <span class="rounded bg-violet-900/60 px-1.5 py-0.2 text-[10px] font-mono text-violet-300 border border-violet-700/50">
                  Historiador IA
                </span>
              </div>
              <p class="text-xs text-zinc-300 leading-relaxed">
                {{ card.contextoOrganizacional }}
              </p>
            </div>
          </div>
        </section>

        <!-- Bloco 4: Ação Sugerida pelo Agente com Reavaliação Programada -->
        <section class="rounded-xl border border-zinc-800 bg-zinc-900/70 p-4">
          <div class="flex items-start gap-3">
            <div class="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-emerald-500/20 border border-emerald-500/30 text-[#CCFF00] shadow-[0_0_12px_rgba(204,255,0,0.2)]">
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
              </svg>
            </div>
            <div class="flex-1 space-y-1">
              <div class="flex items-center justify-between">
                <h5 class="text-xs font-bold uppercase tracking-wider text-white">
                  Plano de Ação Recomendado (Pronto para Homologação no PGR)
                </h5>
                <span class="text-[11px] font-mono font-medium text-[#CCFF00]">
                  Ciclo de Reavaliação: 60 dias
                </span>
              </div>
              <p class="text-xs text-zinc-200 font-medium leading-relaxed">
                {{ card.acaoSugerida }}
              </p>
              <div class="pt-1.5 text-[11px] text-zinc-500">
                <span class="font-semibold text-zinc-400">Fontes Auditáveis:</span>
                {{ card.fontesConsultadas.join(' • ') }}
              </div>
            </div>
          </div>
        </section>

        <!-- Formulário Dinâmico de Edição Rápida (quando clica em Ajustar Ação) -->
        <div *ngIf="showAdjustBox()" class="rounded-xl border border-violet-700/50 bg-[#161420] p-4 space-y-3">
          <h5 class="text-xs font-bold text-violet-200">Personalizar Plano de Ação e Prazo do PGR:</h5>
          <textarea
            [(ngModel)]="customActionText"
            rows="2"
            class="w-full rounded-lg border border-zinc-700 bg-zinc-900 p-2.5 text-xs text-zinc-100 focus:outline-none focus:ring-2 focus:ring-violet-500"
            placeholder="Edite a ação preventiva a ser incluída no PGR..."
          ></textarea>
          <div class="flex items-center gap-3">
            <label class="text-xs text-zinc-400 font-medium">Prazo de Reavaliação:</label>
            <select
              [(ngModel)]="customDeadlineDays"
              class="rounded-md border border-zinc-700 bg-zinc-900 px-2.5 py-1 text-xs text-zinc-200"
            >
              <option [value]="30">30 dias</option>
              <option [value]="60">60 dias (Recomendado NR-1)</option>
              <option [value]="90">90 dias</option>
            </select>
            <button
              type="button"
              (click)="confirmAdjustment()"
              class="rounded-lg bg-[#7C3AED] px-3.5 py-1.5 text-xs font-bold text-white hover:bg-violet-600 ml-auto shadow-[0_0_12px_rgba(124,58,237,0.3)]"
            >
              Confirmar Ajuste e Homologar
            </button>
          </div>
        </div>

        <!-- Formulário de Descarte Justificado -->
        <div *ngIf="showDiscardBox()" class="rounded-xl border border-rose-900/60 bg-rose-950/30 p-4 space-y-2">
          <h5 class="text-xs font-bold text-rose-300">Justificativa Técnica de Descarte (Auditabilidade MTE):</h5>
          <textarea
            [(ngModel)]="discardReason"
            rows="2"
            class="w-full rounded-lg border border-zinc-700 bg-zinc-900 p-2.5 text-xs text-zinc-100 focus:outline-none focus:ring-2 focus:ring-rose-500"
            placeholder="Informe a justificativa do RH para não inclusão no PGR..."
          ></textarea>
          <div class="flex justify-end gap-2">
            <button
              type="button"
              (click)="showDiscardBox.set(false)"
              class="px-2.5 py-1 text-xs text-zinc-400 hover:text-white"
            >
              Cancelar
            </button>
            <button
              type="button"
              (click)="confirmDiscard()"
              class="rounded-md bg-rose-600 px-3 py-1 text-xs font-bold text-white hover:bg-rose-700 shadow-[0_0_10px_rgba(225,29,72,0.3)]"
            >
              Confirmar Descarte
            </button>
          </div>
        </div>

        <!-- Trinca de Deliberação Humana (Human-in-the-Loop) -->
        <footer class="flex flex-wrap items-center justify-between gap-3 border-t border-zinc-800/80 pt-4">
          <div class="flex items-center gap-2 text-xs text-zinc-400">
            <span class="h-2 w-2 rounded-xs bg-[#CCFF00] shadow-[0_0_6px_#CCFF00]"></span>
            <span>Decisão final 100% humana (O agente não altera o PGR sem seu aval).</span>
          </div>

          <div class="flex flex-wrap items-center gap-2.5" *ngIf="!isApproved()">
            <!-- Botão 1: Aprovar e Registrar no PGR (VYTAL Neon Lime) -->
            <button
              type="button"
              (click)="onAprovar()"
              class="inline-flex items-center gap-2 rounded-xl bg-[#CCFF00] px-4 py-2.5 text-xs font-black text-black shadow-[0_0_20px_rgba(204,255,0,0.35)] hover:bg-[#b8e600] active:scale-98 transition-all duration-150 focus:outline-none"
            >
              <svg class="h-4 w-4 text-black stroke-[3]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
              </svg>
              [ Aprovar e Registrar no PGR ]
            </button>

            <!-- Botão 2: Ajustar Ação -->
            <button
              type="button"
              (click)="showAdjustBox.set(!showAdjustBox())"
              class="inline-flex items-center gap-1.5 rounded-xl border border-zinc-700 bg-zinc-900/90 px-3.5 py-2 text-xs font-semibold text-zinc-300 hover:bg-zinc-800 hover:text-white transition-all"
            >
              <svg class="h-3.5 w-3.5 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
              </svg>
              Ajustar Ação
            </button>

            <!-- Botão 3: Descartar -->
            <button
              type="button"
              (click)="showDiscardBox.set(!showDiscardBox())"
              class="inline-flex items-center gap-1 rounded-xl px-3 py-2 text-xs font-medium text-rose-400 hover:bg-rose-950/40 hover:text-rose-300 transition-all"
            >
              Descartar
            </button>
          </div>

          <div *ngIf="isApproved()" class="inline-flex items-center gap-2 text-xs font-mono font-bold text-[#CCFF00] bg-zinc-900/90 border border-emerald-900/50 px-3 py-1.5 rounded-xl">
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
            </svg>
            Protocolo GRO Ativo no PGR (NR-1)
          </div>
        </footer>
      </div>
    </article>
  `,
})
export class RiskFocusCardComponent {
  @Input() card!: RiskCard;
  @Output() resolve = new EventEmitter<{ cardId: string; payload: ResolveRiskCardPayload }>();

  isApproved = signal(false);
  showAdjustBox = signal(false);
  showDiscardBox = signal(false);

  customActionText = '';
  customDeadlineDays = 60;
  discardReason = '';

  formatFator(fator: string): string {
    const map: Record<string, string> = {
      SOBRECARGA_METAS: 'Sobrecarga de Trabalho e Metas Excessivas',
      LIDERANCA_CONFLITO: 'Gestão e Conflitos de Liderança',
      ASSEDIO: 'Assédio Moral e Relações Socioprofissionais',
      JORNADA_EXCESSIVA: 'Jornada Excessiva e Conflito Trabalho-Família',
      OUTRO: 'Fator Psicossocial Geral',
    };
    return map[fator] || fator;
  }

  onAprovar(): void {
    this.isApproved.set(true);
    this.resolve.emit({
      cardId: this.card.cardId,
      payload: {
        actionType: 'APROVAR_PGR',
        reviewerName: 'Mariana Silva (SESMT / RH)',
        deadlineDays: 60,
      },
    });
  }

  confirmAdjustment(): void {
    if (!this.customActionText.trim()) return;
    this.isApproved.set(true);
    this.showAdjustBox.set(false);
    this.resolve.emit({
      cardId: this.card.cardId,
      payload: {
        actionType: 'AJUSTAR_ACAO',
        reviewerName: 'Mariana Silva (SESMT / RH)',
        adjustedActionText: this.customActionText,
        deadlineDays: this.customDeadlineDays,
      },
    });
  }

  confirmDiscard(): void {
    if (!this.discardReason.trim()) return;
    this.showDiscardBox.set(false);
    this.resolve.emit({
      cardId: this.card.cardId,
      payload: {
        actionType: 'DESCARTAR',
        reviewerName: 'Mariana Silva (SESMT / RH)',
        justificationNotes: this.discardReason,
        deadlineDays: 0,
      },
    });
  }
}
