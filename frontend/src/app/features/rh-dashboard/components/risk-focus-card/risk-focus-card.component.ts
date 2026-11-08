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
      class="rounded-xl border border-zinc-800 bg-zinc-900/40 p-6 space-y-5 transition-colors"
      [ngClass]="{
        'opacity-60 bg-zinc-950/80 border-zinc-800/60': isApproved()
      }"
    >
      <!-- Cabeçalho do Card -->
      <header class="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-800/80 pb-4">
        <div class="flex flex-wrap items-center gap-2">
          <!-- Severidade -->
          <span
            class="inline-flex items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-semibold uppercase tracking-wider"
            [ngClass]="{
              'bg-rose-950/40 text-rose-300 border border-rose-800/40': card.riskLevel === 'VERMELHO',
              'bg-amber-950/40 text-amber-300 border border-amber-800/40': card.riskLevel === 'AMARELO',
              'bg-emerald-950/40 text-emerald-300 border border-emerald-800/40': card.riskLevel === 'VERDE'
            }"
          >
            <span
              class="h-1.5 w-1.5 rounded-full"
              [ngClass]="{
                'bg-rose-500': card.riskLevel === 'VERMELHO',
                'bg-amber-400': card.riskLevel === 'AMARELO',
                'bg-emerald-400': card.riskLevel === 'VERDE'
              }"
            ></span>
            Risco {{ card.riskLevel === 'VERMELHO' ? 'Crítico (Alto)' : (card.riskLevel === 'AMARELO' ? 'Moderado (Médio)' : 'Estável') }}
          </span>

          <!-- Score ML -->
          <span
            *ngIf="card.riskScore"
            class="inline-flex items-center gap-1 rounded-md bg-zinc-800/80 px-2.5 py-1 text-xs font-mono font-medium text-zinc-200 border border-zinc-700/80"
          >
            Score ML: <span class="text-white font-bold">{{ card.riskScore }}</span> / 100
          </span>

          <!-- Fator NR-1 -->
          <span class="inline-flex items-center gap-1 rounded-md bg-zinc-800/60 px-2.5 py-1 text-xs font-medium text-zinc-300 border border-zinc-700/60">
            Fator NR-1: {{ formatFator(card.fatorRiscoProvavel) }}
          </span>
        </div>

        <div class="flex flex-wrap items-center gap-2 text-xs">
          <!-- Provedor / Fallback -->
          <span
            class="inline-flex items-center gap-1.5 rounded-md px-2.5 py-1 text-[11px] font-mono border"
            [ngClass]="card.aiFallbackTriggered ? 'bg-amber-950/30 text-amber-300 border-amber-800/40' : 'bg-zinc-800/60 text-zinc-400 border-zinc-700/60'"
          >
            {{ card.aiProviderUsed || 'xgboost + gemini-1.5-pro' }}
            <span *ngIf="card.aiFallbackTriggered" class="font-bold text-amber-400">(Fallback)</span>
          </span>

          <!-- Status do Card -->
          <span
            class="rounded-md px-2.5 py-1 font-mono text-[11px] font-medium border"
            [ngClass]="{
              'bg-zinc-800/80 text-zinc-400 border-zinc-700': card.status === 'ABERTO' && !isApproved(),
              'bg-emerald-950/40 text-emerald-300 border-emerald-800/50': isApproved()
            }"
          >
            {{ isApproved() ? 'HOMOLOGADO NO PGR' : 'AGUARDANDO DELIBERAÇÃO' }}
          </span>
        </div>
      </header>

      <!-- Identificação da Área -->
      <div>
        <h3 class="text-lg font-bold tracking-tight text-white flex items-center gap-2">
          Área: {{ card.areaName }}
          <span class="text-xs font-mono font-normal text-zinc-400 border border-zinc-800 bg-zinc-900 px-2 py-0.5 rounded">
            {{ card.areaHeadcount }} colaboradores
          </span>
        </h3>
        <p class="text-xs text-zinc-400 mt-0.5">
          Conformidade Trabalhista: Portaria MTE nº 1.419/2024 e NR-1 (Capítulo GRO e PGR)
        </p>
      </div>

      <!-- Evidências Quantitativas -->
      <section class="rounded-lg border border-zinc-800 bg-zinc-950/60 p-4 space-y-3">
        <h4 class="text-xs font-semibold uppercase tracking-wider text-zinc-400">
          Evidências Quantitativas Consolidadas (Deltas vs Histórico)
        </h4>

        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div class="rounded-lg bg-zinc-900/60 p-3 border border-zinc-800">
            <span class="block text-[11px] text-zinc-400">Dias de Atestado</span>
            <div class="mt-1 flex items-baseline gap-1">
              <span class="text-xl font-bold font-mono text-rose-400">+45%</span>
              <span class="text-[10px] text-zinc-500 font-mono">trimestre</span>
            </div>
          </div>

          <div class="rounded-lg bg-zinc-900/60 p-3 border border-zinc-800">
            <span class="block text-[11px] text-zinc-400">Horas Extras</span>
            <div class="mt-1 flex items-baseline gap-1">
              <span class="text-xl font-bold font-mono text-rose-400">+60%</span>
              <span class="text-[10px] text-zinc-500 font-mono">sobrecarga</span>
            </div>
          </div>

          <div class="rounded-lg bg-zinc-900/60 p-3 border border-zinc-800">
            <span class="block text-[11px] text-zinc-400">Saídas Voluntárias</span>
            <div class="mt-1 flex items-baseline gap-1">
              <span class="text-xl font-bold font-mono text-amber-400">4</span>
              <span class="text-[10px] text-zinc-500 font-mono">média: 1</span>
            </div>
          </div>

          <div class="rounded-lg bg-zinc-900/60 p-3 border border-zinc-800">
            <span class="block text-[11px] text-zinc-400">Nota Pesquisa Pulso</span>
            <div class="mt-1 flex items-baseline gap-1">
              <span class="text-xl font-bold font-mono text-rose-400">2.4</span>
              <span class="text-[10px] text-zinc-500 line-through font-mono">3.9</span>
            </div>
          </div>
        </div>

        <p class="text-xs text-zinc-300 leading-relaxed border-t border-zinc-800/60 pt-2.5">
          <strong class="text-white">Síntese dos Fatos:</strong>
          {{ card.oQueMudouUltimosMeses }}
        </p>
      </section>

      <!-- Decomposição SHAP -->
      <section
        *ngIf="card.shapBreakdown && card.shapBreakdown.length > 0"
        class="rounded-lg border border-zinc-800 bg-zinc-950/60 p-4 space-y-2.5"
      >
        <div class="flex items-center justify-between">
          <h4 class="text-xs font-semibold uppercase tracking-wider text-zinc-300">
            Auditoria de Explicabilidade Legal (SHAP / XGBoost)
          </h4>
          <span class="text-[10px] font-mono text-zinc-500">
            Sem Caixa-Preta
          </span>
        </div>

        <div class="space-y-2 pt-1">
          <div *ngFor="let item of card.shapBreakdown" class="space-y-1">
            <div class="flex items-center justify-between text-xs">
              <span class="text-zinc-300">
                {{ item.display_name }}
                <span class="text-[10px] font-mono text-zinc-500">({{ item.observed_value }})</span>
              </span>
              <span class="font-mono font-medium text-zinc-200">
                {{ item.contribution_pct }}% do risco
              </span>
            </div>
            <div class="h-1.5 w-full overflow-hidden rounded-full bg-zinc-800">
              <div
                class="h-full rounded-full bg-zinc-400"
                [style.width.%]="item.contribution_pct"
              ></div>
            </div>
          </div>
        </div>
      </section>

      <!-- Hipótese de Contexto -->
      <section class="rounded-lg border border-zinc-800 bg-zinc-950/60 p-4 space-y-1.5">
        <div class="flex items-center justify-between">
          <h4 class="text-xs font-semibold uppercase tracking-wider text-zinc-300">
            Hipótese de Contexto Organizacional
          </h4>
          <span class="text-[10px] font-mono text-zinc-500">Agente Historiador</span>
        </div>
        <p class="text-xs text-zinc-300 leading-relaxed">
          {{ card.contextoOrganizacional }}
        </p>
      </section>

      <!-- Plano de Ação Recomendado -->
      <section class="rounded-lg border border-zinc-800 bg-zinc-950/60 p-4 space-y-1.5">
        <div class="flex items-center justify-between">
          <h4 class="text-xs font-semibold uppercase tracking-wider text-white">
            Plano de Ação Recomendado para o PGR
          </h4>
          <span class="text-[11px] font-mono text-zinc-400">Ciclo de Reavaliação: 60 dias</span>
        </div>
        <p class="text-xs text-zinc-200 leading-relaxed font-medium">
          {{ card.acaoSugerida }}
        </p>
        <div class="pt-1 text-[11px] text-zinc-500">
          <span class="text-zinc-400">Fontes Auditadas:</span>
          {{ card.fontesConsultadas.join(' • ') }}
        </div>
      </section>

      <!-- Formulário de Ajuste -->
      <div *ngIf="showAdjustBox()" class="rounded-lg border border-zinc-700 bg-zinc-950 p-4 space-y-3">
        <h5 class="text-xs font-semibold text-zinc-200">Personalizar Plano de Ação e Prazo:</h5>
        <textarea
          [(ngModel)]="customActionText"
          rows="2"
          class="w-full rounded-md border border-zinc-700 bg-zinc-900 p-2 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-500"
          placeholder="Edite a ação preventiva a ser homologada no PGR..."
        ></textarea>
        <div class="flex items-center gap-3">
          <label class="text-xs text-zinc-400">Prazo:</label>
          <select
            [(ngModel)]="customDeadlineDays"
            class="rounded border border-zinc-700 bg-zinc-900 px-2 py-1 text-xs text-zinc-200"
          >
            <option [value]="30">30 dias</option>
            <option [value]="60">60 dias (Recomendado NR-1)</option>
            <option [value]="90">90 dias</option>
          </select>
          <button
            type="button"
            (click)="confirmAdjustment()"
            class="rounded-md bg-zinc-200 px-3 py-1.5 text-xs font-semibold text-black hover:bg-white ml-auto transition-colors"
          >
            Confirmar Ajuste e Homologar
          </button>
        </div>
      </div>

      <!-- Formulário de Descarte -->
      <div *ngIf="showDiscardBox()" class="rounded-lg border border-rose-900/50 bg-rose-950/20 p-4 space-y-2">
        <h5 class="text-xs font-semibold text-rose-300">Justificativa Técnica de Descarte (Auditabilidade MTE):</h5>
        <textarea
          [(ngModel)]="discardReason"
          rows="2"
          class="w-full rounded-md border border-zinc-700 bg-zinc-900 p-2 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-rose-500"
          placeholder="Informe a justificativa técnica para não inclusão no PGR..."
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
            class="rounded-md bg-rose-600 px-3 py-1 text-xs font-semibold text-white hover:bg-rose-500 transition-colors"
          >
            Confirmar Descarte
          </button>
        </div>
      </div>

      <!-- Rodapé / Deliberação Humana -->
      <footer class="flex flex-wrap items-center justify-between gap-3 border-t border-zinc-800/80 pt-4">
        <div class="text-xs text-zinc-400">
          Decisão 100% humana (O sistema não altera o PGR sem seu aval).
        </div>

        <div class="flex flex-wrap items-center gap-2" *ngIf="!isApproved()">
          <!-- Botão 1: Aprovar -->
          <button
            type="button"
            (click)="onAprovar()"
            class="inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium px-4 py-2 text-xs transition-colors"
          >
            <svg class="h-4 w-4 stroke-[2.5]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
            </svg>
            Aprovar e Registrar no PGR
          </button>

          <!-- Botão 2: Ajustar Ação -->
          <button
            type="button"
            (click)="showAdjustBox.set(!showAdjustBox())"
            class="inline-flex items-center gap-1.5 rounded-lg border border-zinc-700 bg-zinc-800 hover:bg-zinc-700 px-3 py-2 text-xs font-medium text-zinc-200 transition-colors"
          >
            Ajustar Ação
          </button>

          <!-- Botão 3: Descartar -->
          <button
            type="button"
            (click)="showDiscardBox.set(!showDiscardBox())"
            class="inline-flex items-center px-3 py-2 text-xs font-medium text-zinc-400 hover:text-rose-400 transition-colors"
          >
            Descartar
          </button>
        </div>

        <div *ngIf="isApproved()" class="inline-flex items-center gap-1.5 text-xs font-mono font-medium text-emerald-400 bg-zinc-900 border border-zinc-800 px-3 py-1.5 rounded-md">
          <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
          </svg>
          Protocolo GRO Homologado no PGR
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
