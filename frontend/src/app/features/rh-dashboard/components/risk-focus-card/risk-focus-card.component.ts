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
      class="group relative overflow-hidden rounded-2xl border transition-all duration-300 shadow-sm hover:shadow-md"
      [ngClass]="{
        'border-rose-300 bg-white ring-1 ring-rose-200/60': card.riskLevel === 'VERMELHO',
        'border-amber-300 bg-white ring-1 ring-amber-200/60': card.riskLevel === 'AMARELO',
        'border-slate-200 bg-white': card.riskLevel === 'VERDE',
        'opacity-75 bg-slate-50': isApproved()
      }"
    >
      <!-- Faixa lateral indicativa de severidade -->
      <div
        class="absolute left-0 top-0 bottom-0 w-1.5"
        [ngClass]="{
          'bg-rose-500': card.riskLevel === 'VERMELHO',
          'bg-amber-500': card.riskLevel === 'AMARELO',
          'bg-emerald-500': card.riskLevel === 'VERDE'
        }"
      ></div>

      <div class="p-6 pl-7 space-y-5">
        <!-- Header: Severidade, Área, Headcount, Score XGBoost e Provedor de IA -->
        <header class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-4">
          <div class="flex flex-wrap items-center gap-2.5">
            <!-- Pílula de Severidade com Dot Pulsante -->
            <span
              class="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-bold uppercase tracking-wider shadow-xs"
              [ngClass]="{
                'bg-rose-50 text-rose-700 ring-1 ring-rose-300': card.riskLevel === 'VERMELHO',
                'bg-amber-50 text-amber-800 ring-1 ring-amber-300': card.riskLevel === 'AMARELO',
                'bg-emerald-50 text-emerald-800 ring-1 ring-emerald-300': card.riskLevel === 'VERDE'
              }"
            >
              <span
                class="h-2 w-2 rounded-full"
                [ngClass]="{
                  'bg-rose-600 animate-pulse': card.riskLevel === 'VERMELHO' && !isApproved(),
                  'bg-amber-500': card.riskLevel === 'AMARELO' && !isApproved(),
                  'bg-emerald-500': card.riskLevel === 'VERDE' || isApproved()
                }"
              ></span>
              Risco {{ card.riskLevel === 'VERMELHO' ? 'Crítico (Alto)' : (card.riskLevel === 'AMARELO' ? 'Moderado (Médio)' : 'Estável') }}
            </span>

            <!-- Score Matemático do XGBoost -->
            <span
              *ngIf="card.riskScore"
              class="inline-flex items-center gap-1 rounded-md bg-slate-100 px-2.5 py-1 text-xs font-mono font-bold text-slate-800 border border-slate-200"
            >
              Score ML: {{ card.riskScore }} / 100
            </span>

            <!-- Badge Fator de Risco da NR-1 -->
            <span class="inline-flex items-center gap-1 rounded-md bg-indigo-50 px-2.5 py-1 text-xs font-semibold text-indigo-700 ring-1 ring-indigo-200">
              <svg class="h-3.5 w-3.5 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
              Fator NR-1: {{ formatFator(card.fatorRiscoProvavel) }}
            </span>
          </div>

          <div class="flex flex-wrap items-center gap-2 text-xs text-slate-500">
            <!-- Indicador do Provedor de IA e Resiliência -->
            <span
              class="inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[11px] font-medium"
              [ngClass]="card.aiFallbackTriggered ? 'bg-amber-100 text-amber-800 border border-amber-300' : 'bg-slate-100 text-slate-600'"
              [title]="card.aiFallbackTriggered ? 'Plano de contingência ativado: IA substituída automaticamente sem interrupção' : 'Execução nominal'"
            >
              <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
              </svg>
              {{ card.aiProviderUsed || 'xgboost + gemini-1.5-pro' }}
              <span *ngIf="card.aiFallbackTriggered" class="font-bold text-amber-900">(Failover Ativo)</span>
            </span>

            <span
              class="rounded-full px-2.5 py-0.5 font-semibold"
              [ngClass]="{
                'bg-slate-100 text-slate-700': card.status === 'ABERTO' && !isApproved(),
                'bg-emerald-100 text-emerald-800': isApproved()
              }"
            >
              {{ isApproved() ? 'HOMOLOGADO NO PGR' : 'AGUARDANDO DELIBERAÇÃO' }}
            </span>
          </div>
        </header>

        <!-- Título e Subtítulo da Área -->
        <div>
          <h3 class="text-xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
            Área: {{ card.areaName }}
            <span class="text-sm font-normal text-slate-500">
              &bull; {{ card.areaHeadcount }} colaboradores
            </span>
          </h3>
          <p class="text-xs text-slate-500 mt-0.5">
            Monitoramento de conformidade com a Portaria MTE nº 1.419/2024 e NR-1 (Capítulo GRO e PGR)
          </p>
        </div>

        <!-- Bloco 1: Evidências Objetivas Consolidadas (Deltas vs Histórico) -->
        <section class="rounded-xl border border-slate-200/80 bg-slate-50/70 p-4">
          <h4 class="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3 flex items-center gap-1.5">
            <svg class="h-4 w-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
            </svg>
            Evidências Objetivas Consolidadas (Deltas vs Histórico do Time)
          </h4>

          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div class="rounded-lg bg-white p-3 border border-slate-200/70 shadow-xs">
              <span class="block text-[11px] font-medium text-slate-500">Dias de Atestado</span>
              <div class="mt-1 flex items-baseline gap-1">
                <span class="text-xl font-bold font-mono text-rose-600">+45%</span>
                <span class="text-[10px] text-slate-400">vs trimestre</span>
              </div>
            </div>

            <div class="rounded-lg bg-white p-3 border border-slate-200/70 shadow-xs">
              <span class="block text-[11px] font-medium text-slate-500">Horas Extras</span>
              <div class="mt-1 flex items-baseline gap-1">
                <span class="text-xl font-bold font-mono text-rose-600">+60%</span>
                <span class="text-[10px] text-slate-400">sobrecarga</span>
              </div>
            </div>

            <div class="rounded-lg bg-white p-3 border border-slate-200/70 shadow-xs">
              <span class="block text-[11px] font-medium text-slate-500">Saídas Voluntárias</span>
              <div class="mt-1 flex items-baseline gap-1">
                <span class="text-xl font-bold font-mono text-amber-600">4</span>
                <span class="text-[10px] text-slate-400">empresa: 1</span>
              </div>
            </div>

            <div class="rounded-lg bg-white p-3 border border-slate-200/70 shadow-xs">
              <span class="block text-[11px] font-medium text-slate-500">Nota Pesquisa Pulso</span>
              <div class="mt-1 flex items-baseline gap-1">
                <span class="text-xl font-bold font-mono text-rose-600">2.4</span>
                <span class="text-[10px] text-slate-400 line-through">3.9</span>
              </div>
            </div>
          </div>

          <p class="mt-3 text-xs text-slate-600 leading-relaxed">
            <span class="font-semibold text-slate-800">Síntese dos Fatos:</span>
            {{ card.oQueMudouUltimosMeses }}
          </p>
        </section>

        <!-- Bloco 2: Explicabilidade Legal e Decomposição SHAP (O "Cérebro Matemático" XGBoost) -->
        <section
          *ngIf="card.shapBreakdown && card.shapBreakdown.length > 0"
          class="rounded-xl border border-indigo-200/80 bg-indigo-50/40 p-4 space-y-3"
        >
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div class="flex items-center gap-2">
              <span class="flex h-6 w-6 items-center justify-center rounded-lg bg-indigo-600 text-white shadow-xs">
                <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                </svg>
              </span>
              <h4 class="text-xs font-bold uppercase tracking-wider text-indigo-950">
                Auditoria de Explicabilidade Legal (SHAP / NR-1)
              </h4>
            </div>
            <span class="rounded bg-indigo-100 px-2 py-0.5 text-[10px] font-bold text-indigo-800">
              Modelo: XGBoost v1.2 &bull; Sem Caixa-Preta
            </span>
          </div>

          <p class="text-[11px] text-slate-600">
            Decomposição de Shapley exigida pelo MTE para comprovação de nexo causal sem alucinações:
          </p>

          <!-- Barras de Decomposição das Contribuições de Shapley -->
          <div class="space-y-2.5 pt-1">
            <div *ngFor="let item of card.shapBreakdown" class="space-y-1">
              <div class="flex items-center justify-between text-xs">
                <span class="font-semibold text-slate-800 flex items-center gap-1.5">
                  <span class="h-1.5 w-1.5 rounded-full bg-indigo-500"></span>
                  {{ item.display_name }}
                  <span class="text-[10px] font-normal text-slate-500">({{ item.observed_value }})</span>
                </span>
                <span class="font-bold font-mono text-indigo-700">
                  {{ item.contribution_pct }}% do risco
                </span>
              </div>
              <div class="h-2 w-full overflow-hidden rounded-full bg-slate-200">
                <div
                  class="h-full rounded-full transition-all duration-700"
                  [ngClass]="item.contribution_pct > 30 ? 'bg-rose-500' : (item.contribution_pct > 20 ? 'bg-indigo-600' : 'bg-amber-500')"
                  [style.width.%]="item.contribution_pct"
                ></div>
              </div>
            </div>
          </div>
        </section>

        <!-- Bloco 3: Hipótese de Contexto (Motor de IA / Correlação Temporal) -->
        <section class="rounded-xl border border-indigo-200 bg-gradient-to-r from-indigo-50/70 via-white to-indigo-50/40 p-4">
          <div class="flex items-start gap-3">
            <div class="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-indigo-600 text-white shadow-xs">
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
            </div>
            <div class="space-y-1">
              <div class="flex items-center gap-2">
                <h5 class="text-xs font-bold uppercase tracking-wider text-indigo-900">
                  Hipótese de Contexto Organizacional (Digital Worker Pulso)
                </h5>
                <span class="rounded bg-indigo-100 px-1.5 py-0.2 text-[10px] font-semibold text-indigo-700">
                  Correlação Temporal
                </span>
              </div>
              <p class="text-xs text-slate-700 leading-relaxed">
                {{ card.contextoOrganizacional }}
              </p>
            </div>
          </div>
        </section>

        <!-- Bloco 4: Ação Sugerida pelo Agente com Reavaliação Programada -->
        <section class="rounded-xl border border-emerald-200 bg-emerald-50/50 p-4">
          <div class="flex items-start gap-3">
            <div class="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-emerald-600 text-white shadow-xs">
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
              </svg>
            </div>
            <div class="flex-1 space-y-1">
              <div class="flex items-center justify-between">
                <h5 class="text-xs font-bold uppercase tracking-wider text-emerald-900">
                  Plano de Ação Recomendado (Pronto para o PGR)
                </h5>
                <span class="text-[11px] font-medium text-emerald-800">
                  Ciclo de Reavaliação: 60 dias
                </span>
              </div>
              <p class="text-xs text-slate-700 font-medium leading-relaxed">
                {{ card.acaoSugerida }}
              </p>
              <div class="pt-1 text-[11px] text-slate-500">
                <span class="font-semibold text-slate-700">Fontes Auditáveis:</span>
                {{ card.fontesConsultadas.join(' • ') }}
              </div>
            </div>
          </div>
        </section>

        <!-- Formulário Dinâmico de Edição Rápida (quando usuário clica em Ajustar Ação) -->
        <div *ngIf="showAdjustBox()" class="rounded-xl border border-indigo-300 bg-indigo-50/50 p-4 space-y-3">
          <h5 class="text-xs font-bold text-indigo-900">Personalizar Plano de Ação e Prazo do PGR:</h5>
          <textarea
            [(ngModel)]="customActionText"
            rows="2"
            class="w-full rounded-lg border border-indigo-200 bg-white p-2.5 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Edite a ação preventiva a ser incluída no PGR..."
          ></textarea>
          <div class="flex items-center gap-3">
            <label class="text-xs text-slate-600 font-medium">Prazo de Reavaliação:</label>
            <select
              [(ngModel)]="customDeadlineDays"
              class="rounded-md border border-slate-300 bg-white px-2.5 py-1 text-xs text-slate-700"
            >
              <option [value]="30">30 dias</option>
              <option [value]="60">60 dias (Recomendado NR-1)</option>
              <option [value]="90">90 dias</option>
            </select>
            <button
              type="button"
              (click)="confirmAdjustment()"
              class="rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-bold text-white hover:bg-indigo-700 ml-auto"
            >
              Confirmar Ajuste e Aprovar
            </button>
          </div>
        </div>

        <!-- Formulário de Descarte Justificado -->
        <div *ngIf="showDiscardBox()" class="rounded-xl border border-rose-200 bg-rose-50/60 p-4 space-y-2">
          <h5 class="text-xs font-bold text-rose-900">Justificativa Técnica de Descarte (Exigida para Auditoria):</h5>
          <textarea
            [(ngModel)]="discardReason"
            rows="2"
            class="w-full rounded-lg border border-rose-200 bg-white p-2.5 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-rose-500"
            placeholder="Informe a justificativa do RH para não inclusão no PGR..."
          ></textarea>
          <div class="flex justify-end gap-2">
            <button
              type="button"
              (click)="showDiscardBox.set(false)"
              class="px-2.5 py-1 text-xs text-slate-600 hover:text-slate-800"
            >
              Cancelar
            </button>
            <button
              type="button"
              (click)="confirmDiscard()"
              class="rounded-md bg-rose-600 px-3 py-1 text-xs font-bold text-white hover:bg-rose-700"
            >
              Confirmar Descarte
            </button>
          </div>
        </div>

        <!-- Trinca de Deliberação Humana (Human-in-the-Loop) -->
        <footer class="flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-4">
          <div class="flex items-center gap-2 text-xs text-slate-500">
            <svg class="h-4 w-4 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
            <span>Decisão final 100% humana (O agente não altera o PGR sem seu aval).</span>
          </div>

          <div class="flex flex-wrap items-center gap-2" *ngIf="!isApproved()">
            <!-- Botão 1: Aprovar e Registrar no PGR (Proeminente Emerald) -->
            <button
              type="button"
              (click)="onAprovar()"
              class="inline-flex items-center gap-1.5 rounded-xl bg-emerald-600 px-4 py-2.5 text-xs font-bold text-white shadow-sm hover:bg-emerald-700 active:scale-98 transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-1"
            >
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
              </svg>
              Aprovar e Registrar no PGR
            </button>

            <!-- Botão 2: Ajustar Ação -->
            <button
              type="button"
              (click)="showAdjustBox.set(!showAdjustBox())"
              class="inline-flex items-center gap-1.5 rounded-xl border border-slate-300 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 shadow-xs hover:bg-slate-50 hover:text-slate-900 transition-all"
            >
              <svg class="h-3.5 w-3.5 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
              </svg>
              Ajustar Ação
            </button>

            <!-- Botão 3: Descartar -->
            <button
              type="button"
              (click)="showDiscardBox.set(!showDiscardBox())"
              class="inline-flex items-center gap-1 rounded-xl px-3 py-2 text-xs font-medium text-rose-600 hover:bg-rose-50 transition-all"
            >
              Descartar
            </button>
          </div>

          <!-- Feedback de Aprovação Concluída -->
          <div *ngIf="isApproved()" class="inline-flex items-center gap-2 rounded-xl bg-emerald-100 px-4 py-2 text-xs font-bold text-emerald-800">
            <svg class="h-4 w-4 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
            </svg>
            Plano de ação formalizado e incluído no Inventário PGR
          </div>
        </footer>
      </div>
    </article>
  `,
})
export class RiskFocusCardComponent {
  @Input({ required: true }) card!: RiskCard;
  @Output() resolve = new EventEmitter<{ cardId: string; payload: ResolveRiskCardPayload }>();

  isApproved = signal(false);
  showAdjustBox = signal(false);
  showDiscardBox = signal(false);

  customActionText = '';
  customDeadlineDays = 60;
  discardReason = '';

  formatFator(fator: string): string {
    const mapa: Record<string, string> = {
      SOBRECARGA_METAS: 'Sobrecarga e Metas Excessivas',
      LIDERANCA_CONFLITO: 'Conflito com Liderança',
      ASSEDIO: 'Assédio / Risco Psicossocial Grave',
      JORNADAS_LONGAS: 'Jornadas Excessivas',
      FALTA_CLAREZA_PAPEL: 'Falta de Clareza de Papel',
      FALTA_AUTONOMIA: 'Baixa Autonomia',
      INSEGURANCA_TRABALHO: 'Insegurança no Trabalho',
      ESTAVEL_SEM_FATOR: 'Estável (Sem Fator)',
    };
    return mapa[fator] || fator;
  }

  onAprovar(): void {
    this.isApproved.set(true);
    this.resolve.emit({
      cardId: this.card.cardId,
      payload: {
        actionType: 'APROVAR_PGR',
        reviewerName: 'Juliana Costa (Especialista RH / SESMT)',
        deadlineDays: 60,
      },
    });
  }

  confirmAdjustment(): void {
    this.isApproved.set(true);
    this.showAdjustBox.set(false);
    this.resolve.emit({
      cardId: this.card.cardId,
      payload: {
        actionType: 'AJUSTAR_ACAO',
        reviewerName: 'Juliana Costa (Especialista RH / SESMT)',
        adjustedActionText: this.customActionText || this.card.acaoSugerida,
        deadlineDays: this.customDeadlineDays,
      },
    });
  }

  confirmDiscard(): void {
    this.showDiscardBox.set(false);
    this.resolve.emit({
      cardId: this.card.cardId,
      payload: {
        actionType: 'DESCARTAR',
        reviewerName: 'Juliana Costa (Especialista RH / SESMT)',
        deadlineDays: 0,
        justificationNotes: this.discardReason || 'Descarte fundamentado por validação prévia com gestão.',
      },
    });
  }
}
