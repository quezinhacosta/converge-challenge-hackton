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
      class="relative overflow-hidden rounded-2xl border border-zinc-700/80 bg-gradient-to-b from-zinc-900/90 via-[#0e0e14] to-zinc-950/90 p-8 space-y-6 shadow-2xl backdrop-blur-xl transition-all duration-300 hover:border-zinc-600"
      [ngClass]="{
        'opacity-60 bg-zinc-950/80 border-zinc-800/60': isApproved()
      }"
    >
      <!-- Faixa Lateral com Efeito Gradiente Sutil -->
      <div
        class="absolute left-0 top-0 bottom-0 w-2"
        [ngClass]="{
          'bg-gradient-to-b from-rose-500 via-violet-600 to-indigo-600': card.riskLevel === 'VERMELHO',
          'bg-gradient-to-b from-amber-400 to-orange-500': card.riskLevel === 'AMARELO',
          'bg-gradient-to-b from-emerald-400 to-teal-500': card.riskLevel === 'VERDE'
        }"
      ></div>

      <!-- Cabeçalho do Card com Informações Claras e Grandes -->
      <header class="flex flex-wrap items-center justify-between gap-4 border-b border-zinc-800/80 pb-5 pl-2">
        <div class="flex flex-wrap items-center gap-3">
          <!-- Pílula de Severidade -->
          <span
            class="inline-flex items-center gap-2 rounded-xl px-4 py-1.5 text-xs font-black uppercase tracking-wider shadow-sm"
            [ngClass]="{
              'bg-rose-950/70 text-rose-300 border border-rose-700/60': card.riskLevel === 'VERMELHO',
              'bg-amber-950/70 text-amber-300 border border-amber-700/60': card.riskLevel === 'AMARELO',
              'bg-emerald-950/70 text-emerald-300 border border-emerald-700/60': card.riskLevel === 'VERDE'
            }"
          >
            <span class="relative flex h-2 w-2">
              <span
                *ngIf="!isApproved()"
                class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
                [ngClass]="card.riskLevel === 'VERMELHO' ? 'bg-rose-400' : 'bg-amber-400'"
              ></span>
              <span
                class="relative inline-flex rounded-full h-2 w-2"
                [ngClass]="{
                  'bg-rose-500': card.riskLevel === 'VERMELHO',
                  'bg-amber-400': card.riskLevel === 'AMARELO',
                  'bg-emerald-400': card.riskLevel === 'VERDE'
                }"
              ></span>
            </span>
            Risco {{ card.riskLevel === 'VERMELHO' ? 'Crítico (Alto)' : (card.riskLevel === 'AMARELO' ? 'Moderado (Médio)' : 'Estável') }}
          </span>

          <!-- Score ML de Alta Precisão -->
          <span
            *ngIf="card.riskScore"
            class="inline-flex items-center gap-1.5 rounded-xl bg-zinc-800/90 px-3.5 py-1.5 text-xs font-mono font-bold text-zinc-100 border border-zinc-700 shadow-inner"
          >
            Score Matemático: <span class="text-white text-sm font-black">{{ card.riskScore }}</span> / 100
          </span>

          <!-- Fator NR-1 -->
          <span class="inline-flex items-center gap-1.5 rounded-xl bg-violet-950/40 px-3.5 py-1.5 text-xs font-semibold text-violet-200 border border-violet-800/50">
            Fator NR-1: {{ formatFator(card.fatorRiscoProvavel) }}
          </span>
        </div>

        <div class="flex flex-wrap items-center gap-2.5 text-xs">
          <!-- Provedor / Fallback -->
          <span
            class="inline-flex items-center gap-1.5 rounded-lg px-3 py-1 font-mono text-xs border"
            [ngClass]="card.aiFallbackTriggered ? 'bg-amber-950/40 text-amber-200 border-amber-700/60 font-bold' : 'bg-zinc-800/80 text-zinc-300 border-zinc-700'"
          >
            <span class="h-1.5 w-1.5 rounded-full bg-teal-400"></span>
            {{ card.aiProviderUsed || 'xgboost + gemini-1.5-pro' }}
            <span *ngIf="card.aiFallbackTriggered" class="text-amber-400 font-bold">(Fallback Ativo)</span>
          </span>

          <!-- Status do Card -->
          <span
            class="rounded-lg px-3.5 py-1 font-mono text-xs font-bold border"
            [ngClass]="{
              'bg-zinc-800 text-zinc-300 border-zinc-700': card.status === 'ABERTO' && !isApproved(),
              'bg-emerald-950/60 text-emerald-300 border-emerald-700 shadow-sm': isApproved()
            }"
          >
            {{ isApproved() ? 'HOMOLOGADO NO PGR' : 'AGUARDANDO DELIBERAÇÃO' }}
          </span>
        </div>
      </header>

      <!-- Identificação da Área com Letras Grandes e Nítidas -->
      <div class="pl-2">
        <h3 class="text-2xl font-black tracking-tight text-white flex items-center gap-3">
          <span>Área: {{ card.areaName }}</span>
          <span class="text-xs font-mono font-semibold text-zinc-300 border border-zinc-700 bg-zinc-800/90 px-3 py-1 rounded-lg">
            {{ card.areaHeadcount }} colaboradores
          </span>
        </h3>
        <p class="text-sm text-zinc-300 font-medium mt-1">
          Conformidade Trabalhista: Portaria MTE nº 1.419/2024 e NR-1 (Capítulo GRO e PGR)
        </p>
      </div>

      <!-- Evidências Quantitativas (Cards Grandes com Métricas Claras) -->
      <section class="rounded-2xl border border-zinc-800 bg-[#09090d]/90 p-6 space-y-4 shadow-inner">
        <h4 class="text-xs font-bold uppercase tracking-wider text-zinc-300 flex items-center gap-2">
          <svg class="h-4 w-4 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
          </svg>
          Evidências Quantitativas Consolidadas (Deltas vs Histórico do Setor)
        </h4>

        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div class="rounded-xl bg-zinc-900/80 p-4 border border-zinc-800 shadow-sm">
            <span class="block text-xs font-semibold text-zinc-300">Dias de Atestado</span>
            <div class="mt-1.5 flex items-baseline gap-1.5">
              <span class="text-3xl font-black font-mono text-rose-400">+45%</span>
              <span class="text-xs text-zinc-400 font-mono">trimestre</span>
            </div>
          </div>

          <div class="rounded-xl bg-zinc-900/80 p-4 border border-zinc-800 shadow-sm">
            <span class="block text-xs font-semibold text-zinc-300">Horas Extras</span>
            <div class="mt-1.5 flex items-baseline gap-1.5">
              <span class="text-3xl font-black font-mono text-rose-400">+60%</span>
              <span class="text-xs text-zinc-400 font-mono">sobrecarga</span>
            </div>
          </div>

          <div class="rounded-xl bg-zinc-900/80 p-4 border border-zinc-800 shadow-sm">
            <span class="block text-xs font-semibold text-zinc-300">Saídas Voluntárias</span>
            <div class="mt-1.5 flex items-baseline gap-1.5">
              <span class="text-3xl font-black font-mono text-amber-400">4</span>
              <span class="text-xs text-zinc-400 font-mono">média: 1</span>
            </div>
          </div>

          <div class="rounded-xl bg-zinc-900/80 p-4 border border-zinc-800 shadow-sm">
            <span class="block text-xs font-semibold text-zinc-300">Nota Pesquisa Pulso</span>
            <div class="mt-1.5 flex items-baseline gap-1.5">
              <span class="text-3xl font-black font-mono text-rose-400">2.4</span>
              <span class="text-xs text-zinc-400 line-through font-mono">3.9</span>
            </div>
          </div>
        </div>

        <p class="text-sm text-zinc-200 leading-relaxed border-t border-zinc-800/80 pt-3">
          <strong class="text-white">Síntese dos Fatos Observados:</strong>
          {{ card.oQueMudouUltimosMeses }}
        </p>
      </section>

      <!-- Decomposição SHAP (Explicabilidade Clara com Barras em Gradiente) -->
      <section
        *ngIf="card.shapBreakdown && card.shapBreakdown.length > 0"
        class="rounded-2xl border border-zinc-800 bg-[#09090d]/90 p-6 space-y-3.5 shadow-inner"
      >
        <div class="flex items-center justify-between">
          <h4 class="text-xs font-bold uppercase tracking-wider text-violet-300 flex items-center gap-2">
            <svg class="h-4 w-4 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
            </svg>
            Auditoria de Explicabilidade Legal (SHAP / XGBoost)
          </h4>
          <span class="text-xs font-mono font-semibold text-zinc-400 bg-zinc-800/80 px-2.5 py-0.5 rounded border border-zinc-700">
            Nexo Causal Matemático
          </span>
        </div>

        <div class="space-y-3 pt-1">
          <div *ngFor="let item of card.shapBreakdown" class="space-y-1.5">
            <div class="flex items-center justify-between text-sm font-semibold">
              <span class="text-zinc-200">
                {{ item.display_name }}
                <span class="text-xs font-mono text-zinc-400 font-normal">({{ item.observed_value }})</span>
              </span>
              <span class="font-mono font-bold text-teal-300">
                {{ item.contribution_pct }}% do risco
              </span>
            </div>
            <div class="h-2.5 w-full overflow-hidden rounded-full bg-zinc-800/90 shadow-inner">
              <div
                class="h-full rounded-full bg-gradient-to-r from-violet-600 via-indigo-500 to-teal-400 transition-all duration-700"
                [style.width.%]="item.contribution_pct"
              ></div>
            </div>
          </div>
        </div>
      </section>

      <!-- Hipótese de Contexto Organizacional -->
      <section class="rounded-2xl border border-zinc-800 bg-[#09090d]/90 p-6 space-y-2 shadow-inner">
        <div class="flex items-center justify-between">
          <h4 class="text-xs font-bold uppercase tracking-wider text-indigo-300 flex items-center gap-2">
            <span class="h-2 w-2 rounded-full bg-indigo-400 animate-pulse"></span>
            Hipótese de Contexto Organizacional
          </h4>
          <span class="text-xs font-mono text-zinc-400">Agente Historiador</span>
        </div>
        <p class="text-sm text-zinc-200 leading-relaxed font-medium">
          {{ card.contextoOrganizacional }}
        </p>
      </section>

      <!-- Plano de Ação Recomendado -->
      <section class="rounded-2xl border border-zinc-800 bg-[#09090d]/90 p-6 space-y-2 shadow-inner">
        <div class="flex items-center justify-between">
          <h4 class="text-xs font-bold uppercase tracking-wider text-teal-300 flex items-center gap-2">
            <span class="h-2 w-2 rounded-full bg-teal-400"></span>
            Plano de Ação Recomendado para o PGR
          </h4>
          <span class="text-xs font-mono font-bold text-teal-400">Ciclo de Reavaliação: 60 dias</span>
        </div>
        <p class="text-sm text-white leading-relaxed font-semibold">
          {{ card.acaoSugerida }}
        </p>
        <div class="pt-2 text-xs text-zinc-400 border-t border-zinc-800/80">
          <span class="font-bold text-zinc-300">Fontes Auditadas:</span>
          {{ card.fontesConsultadas.join(' • ') }}
        </div>
      </section>

      <!-- Formulário de Ajuste Dinâmico -->
      <div *ngIf="showAdjustBox()" class="rounded-2xl border border-zinc-700 bg-zinc-950 p-6 space-y-4 shadow-xl">
        <h5 class="text-sm font-bold text-zinc-100">Personalizar Plano de Ação e Prazo do PGR:</h5>
        <textarea
          [(ngModel)]="customActionText"
          rows="2"
          class="w-full rounded-xl border border-zinc-700 bg-zinc-900 p-3 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-violet-500"
          placeholder="Edite a ação preventiva a ser homologada no PGR..."
        ></textarea>
        <div class="flex items-center gap-4">
          <label class="text-xs text-zinc-300 font-semibold">Prazo de Reavaliação:</label>
          <select
            [(ngModel)]="customDeadlineDays"
            class="rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-1.5 text-xs text-zinc-200"
          >
            <option [value]="30">30 dias</option>
            <option [value]="60">60 dias (Recomendado NR-1)</option>
            <option [value]="90">90 dias</option>
          </select>
          <button
            type="button"
            (click)="confirmAdjustment()"
            class="rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 px-5 py-2 text-xs font-bold text-white ml-auto shadow-md transition-all"
          >
            Confirmar Ajuste e Homologar
          </button>
        </div>
      </div>

      <!-- Formulário de Descarte Técnico -->
      <div *ngIf="showDiscardBox()" class="rounded-2xl border border-rose-900/60 bg-rose-950/30 p-6 space-y-3 shadow-xl">
        <h5 class="text-sm font-bold text-rose-300">Justificativa Técnica de Descarte (Auditabilidade MTE):</h5>
        <textarea
          [(ngModel)]="discardReason"
          rows="2"
          class="w-full rounded-xl border border-zinc-700 bg-zinc-900 p-3 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-rose-500"
          placeholder="Informe a justificativa técnica para não inclusão no PGR..."
        ></textarea>
        <div class="flex justify-end gap-3">
          <button
            type="button"
            (click)="showDiscardBox.set(false)"
            class="px-4 py-2 text-xs font-bold text-zinc-300 hover:text-white"
          >
            Cancelar
          </button>
          <button
            type="button"
            (click)="confirmDiscard()"
            class="rounded-xl bg-rose-600 hover:bg-rose-500 px-5 py-2 text-xs font-bold text-white transition-all shadow-md"
          >
            Confirmar Descarte
          </button>
        </div>
      </div>

      <!-- Rodapé / Deliberação Humana (Botões de Alto Impacto) -->
      <footer class="flex flex-wrap items-center justify-between gap-4 border-t border-zinc-800/80 pt-5 pl-2">
        <div class="text-xs text-zinc-300 font-medium">
          Decisão 100% humana (O sistema não altera o PGR sem seu aval).
        </div>

        <div class="flex flex-wrap items-center gap-3" *ngIf="!isApproved()">
          <!-- Botão 1: Aprovar e Registrar no PGR (Gradiente Marcante) -->
          <button
            type="button"
            (click)="onAprovar()"
            class="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-500 hover:from-emerald-500 hover:to-teal-400 text-white font-extrabold px-6 py-3 text-xs shadow-xl shadow-emerald-950/70 hover:scale-[1.02] active:scale-95 transition-all"
          >
            <svg class="h-4 w-4 stroke-[3]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
            </svg>
            Aprovar e Registrar no PGR
          </button>

          <!-- Botão 2: Ajustar Ação -->
          <button
            type="button"
            (click)="showAdjustBox.set(!showAdjustBox())"
            class="inline-flex items-center gap-2 rounded-xl border border-zinc-700 bg-zinc-800/90 hover:bg-zinc-700 hover:border-zinc-600 px-5 py-3 text-xs font-bold text-zinc-100 shadow-md transition-all"
          >
            Ajustar Ação
          </button>

          <!-- Botão 3: Descartar -->
          <button
            type="button"
            (click)="showDiscardBox.set(!showDiscardBox())"
            class="inline-flex items-center px-4 py-3 text-xs font-bold text-zinc-400 hover:text-rose-400 transition-colors"
          >
            Descartar
          </button>
        </div>

        <div *ngIf="isApproved()" class="inline-flex items-center gap-2 text-xs font-mono font-bold text-emerald-400 bg-zinc-900 border border-emerald-900/60 px-4 py-2 rounded-xl shadow-md">
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
          </svg>
          Protocolo GRO Homologado no PGR (NR-1)
        </div>
      </footer>
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
      SOBRECARGA_METAS: 'Sobrecarga de Metas',
      LIDERANCA_CONFLITO: 'Gestão e Conflitos',
      ASSEDIO: 'Assédio / Ética',
      JORNADA_EXCESSIVA: 'Jornada Excessiva',
      OUTRO: 'Fator Geral',
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
