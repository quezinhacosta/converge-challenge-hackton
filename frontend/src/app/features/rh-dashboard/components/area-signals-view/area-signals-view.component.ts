import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AreaHistoryComparison } from '../../../../core/models/signals.model';

@Component({
  selector: 'app-area-signals-view',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div *ngIf="comparison">
      <!-- Protecao de Privacidade (Quorom < 5 pessoas) -->
      <div
        *ngIf="comparison.isAnonymized"
        class="rounded-xl border border-amber-200 bg-amber-50 p-6 text-amber-900"
      >
        <h3 class="font-bold">
          Dados Ocultados para Proteção de Privacidade (Quórum &lt; 5 pessoas)
        </h3>
        <p class="mt-2 text-sm">
          A área <strong>{{ comparison.areaName }}</strong> possui apenas
          {{ comparison.headcount }} colaboradores. Para impedir a identificação de pessoas por
          exclusão, os indicadores agregados não são exibidos nesta visualização.
        </p>
      </div>

      <!-- Exibicao Normal -->
      <div
        *ngIf="!comparison.isAnonymized"
        class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
      >
        <h3 class="text-lg font-bold text-slate-900">
          Painel de Sinais: {{ comparison.areaName }} ({{ comparison.headcount }} pessoas)
        </h3>
        <div class="mt-4 grid grid-cols-2 gap-4 text-sm">
          <div class="rounded-lg bg-slate-50 p-3">
            <div class="text-xs text-slate-500">Variação de Dias de Atestado</div>
            <div class="mt-1 text-xl font-bold text-slate-800">
              {{ comparison.variacaoDiasAtestadoPct > 0 ? '+' : '' }}
              {{ comparison.variacaoDiasAtestadoPct }}%
            </div>
          </div>
          <div class="rounded-lg bg-slate-50 p-3">
            <div class="text-xs text-slate-500">Variação de Horas Extras</div>
            <div class="mt-1 text-xl font-bold text-slate-800">
              {{ comparison.variacaoHorasExtrasPct > 0 ? '+' : '' }}
              {{ comparison.variacaoHorasExtrasPct }}%
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
})
export class AreaSignalsViewComponent {
  @Input({ required: true }) comparison!: AreaHistoryComparison;
}
