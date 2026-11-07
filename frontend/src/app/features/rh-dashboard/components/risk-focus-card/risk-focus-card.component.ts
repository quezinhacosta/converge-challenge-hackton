import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RiskCard, ResolveRiskCardPayload } from '../../../../core/models/risk-card.model';

@Component({
  selector: 'app-risk-focus-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="rounded-xl border border-rose-200 bg-white p-6 shadow-sm" *ngIf="card">
      <div class="flex items-center justify-between border-b border-slate-100 pb-3">
        <div>
          <span class="inline-flex items-center rounded-full bg-rose-100 px-2.5 py-0.5 text-xs font-semibold text-rose-800">
            ATENÇÃO {{ card.riskLevel }}
          </span>
          <h3 class="mt-1 text-lg font-bold text-slate-900">
            Área: {{ card.areaName }} ({{ card.areaHeadcount }} pessoas)
          </h3>
        </div>
        <span class="text-xs text-slate-400">Status: {{ card.status }}</span>
      </div>

      <div class="mt-4 space-y-3 text-sm text-slate-700">
        <div>
          <strong class="text-slate-900">O que mudou nos últimos 3 meses:</strong>
          {{ card.oQueMudouUltimosMeses }}
        </div>
        <div>
          <strong class="text-slate-900">Contexto:</strong>
          {{ card.contextoOrganizacional }}
        </div>
        <div>
          <strong class="text-slate-900">Fator de risco provável:</strong>
          <span class="font-semibold text-indigo-700">{{ card.fatorRiscoProvavel }}</span>
        </div>
        <div class="rounded-lg bg-amber-50 p-3 text-amber-900">
          <strong>Ação sugerida:</strong> {{ card.acaoSugerida }}
        </div>
        <div class="text-xs text-slate-500">
          <strong>Fontes consultadas:</strong> {{ card.fontesConsultadas.join(', ') }}
        </div>
      </div>

      <div class="mt-6 flex flex-wrap gap-2 border-t border-slate-100 pt-4">
        <button
          type="button"
          class="rounded-md bg-emerald-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-emerald-700"
          (click)="onAprovar()"
        >
          Aprovar e registrar no PGR
        </button>
        <button
          type="button"
          class="rounded-md bg-slate-100 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-200"
          (click)="onAjustar()"
        >
          Ajustar ação
        </button>
        <button
          type="button"
          class="rounded-md bg-rose-50 px-3 py-1.5 text-xs font-medium text-rose-700 hover:bg-rose-100"
          (click)="onDescartar()"
        >
          Descartar com justificativa
        </button>
      </div>
    </div>
  `,
})
export class RiskFocusCardComponent {
  @Input({ required: true }) card!: RiskCard;
  @Output() resolve = new EventEmitter<{ cardId: string; payload: ResolveRiskCardPayload }>();

  onAprovar(): void {
    this.resolve.emit({
      cardId: this.card.cardId,
      payload: {
        actionType: 'APROVAR_PGR',
        reviewerName: 'Analista de RH',
        deadlineDays: 60,
      },
    });
  }

  onAjustar(): void {
    this.resolve.emit({
      cardId: this.card.cardId,
      payload: {
        actionType: 'AJUSTAR_ACAO',
        reviewerName: 'Analista de RH',
        deadlineDays: 60,
      },
    });
  }

  onDescartar(): void {
    this.resolve.emit({
      cardId: this.card.cardId,
      payload: {
        actionType: 'DESCARTAR',
        reviewerName: 'Analista de RH',
        deadlineDays: 0,
        justificationNotes: 'Sem evidências suficientes após alinhamento com liderança.',
      },
    });
  }
}
