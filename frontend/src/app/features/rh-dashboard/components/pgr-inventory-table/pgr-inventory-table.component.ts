import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PgrInventoryItem } from '../../../../core/models/nr1.model';

@Component({
  selector: 'app-pgr-inventory-table',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <div class="flex items-center justify-between border-b border-slate-200 pb-4">
        <div>
          <h2 class="text-xl font-bold text-slate-900">
            Inventário de Riscos e Plano de Ação (PGR / NR-1)
          </h2>
          <p className="mt-1 text-sm text-slate-500">
            Documentação formal e auditável exigida pela Portaria MTE nº 1.419/2024.
          </p>
        </div>
      </div>

      <div class="mt-4 overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-200 text-left text-sm">
          <thead class="bg-slate-50 text-xs font-semibold text-slate-700">
            <tr>
              <th class="px-4 py-3">Área</th>
              <th class="px-4 py-3">Fator Psicossocial</th>
              <th class="px-4 py-3">Nível</th>
              <th class="px-4 py-3">Plano de Ação</th>
              <th class="px-4 py-3">Responsável</th>
              <th class="px-4 py-3">Prazo</th>
              <th class="px-4 py-3">Acompanhamento</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200">
            <tr *ngFor="let item of items" class="hover:bg-slate-50">
              <td class="px-4 py-3 font-medium text-slate-900">{{ item.areaName }}</td>
              <td class="px-4 py-3 text-slate-600">{{ item.factor }}</td>
              <td class="px-4 py-3">
                <span class="rounded px-2 py-0.5 text-xs font-semibold bg-rose-100 text-rose-800">
                  {{ item.severityLevel }}
                </span>
              </td>
              <td class="px-4 py-3 text-slate-700">{{ item.actionPlanDescription }}</td>
              <td class="px-4 py-3 text-slate-600">{{ item.responsiblePerson }}</td>
              <td class="px-4 py-3 text-slate-600">{{ item.deadlineDate }}</td>
              <td class="px-4 py-3">
                <button
                  type="button"
                  (click)="onReavaliar(item.itemId)"
                  class="text-xs text-indigo-600 hover:text-indigo-800 font-medium"
                >
                  Reavaliar (60 dias)
                </button>
              </td>
            </tr>
            <tr *ngIf="items.length === 0">
              <td colspan="7" class="px-4 py-6 text-center text-sm text-slate-400">
                Nenhum risco aprovado no inventário do PGR até o momento.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
})
export class PgrInventoryTableComponent {
  @Input() items: PgrInventoryItem[] = [];
  @Output() reassess = new EventEmitter<string>();

  onReavaliar(itemId: string): void {
    this.reassess.emit(itemId);
  }
}
