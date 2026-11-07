import { Component, Input, Output, EventEmitter, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PgrInventoryItem, RiskLevel, PsychosocialRiskFactor } from '../../../../core/models/nr1.model';

@Component({
  selector: 'app-pgr-inventory-table',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <!-- Cabeçalho Executivo do PGR -->
      <header class="border-b border-slate-100 bg-slate-50/70 p-6">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div class="flex items-center gap-2">
              <span class="inline-flex items-center rounded-md bg-indigo-50 px-2.5 py-0.5 text-xs font-bold text-indigo-700 border border-indigo-200">
                PGR &bull; Programa de Gerenciamento de Riscos
              </span>
              <span class="text-xs text-slate-500">Portaria MTE nº 1.419/2024</span>
            </div>
            <h2 class="mt-1 text-xl font-bold tracking-tight text-slate-900">
              Inventário Oficial de Riscos Psicossociais & Plano de Ação
            </h2>
            <p class="text-xs text-slate-500 mt-0.5">
              Registros auditáveis com cronograma, responsáveis e ciclos de reavaliação de eficácia (60 dias).
            </p>
          </div>

          <div class="flex items-center gap-2">
            <span class="inline-flex items-center gap-1.5 rounded-lg bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 border border-slate-200 shadow-xs">
              <span class="h-2 w-2 rounded-full bg-emerald-500"></span>
              {{ getActiveCount() }} Ações em Monitoramento
            </span>
          </div>
        </div>

        <!-- Barra de Filtros e Busca -->
        <div class="mt-4 flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-200/60">
          <div class="flex items-center gap-2">
            <button
              type="button"
              (click)="filterStatus.set('ALL')"
              class="rounded-lg px-3 py-1 text-xs font-semibold transition-colors"
              [ngClass]="filterStatus() === 'ALL' ? 'bg-indigo-600 text-white' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-100'"
            >
              Todos ({{ items.length }})
            </button>
            <button
              type="button"
              (click)="filterStatus.set('OPEN')"
              class="rounded-lg px-3 py-1 text-xs font-semibold transition-colors"
              [ngClass]="filterStatus() === 'OPEN' ? 'bg-indigo-600 text-white' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-100'"
            >
              Em Acompanhamento
            </button>
            <button
              type="button"
              (click)="filterStatus.set('CLOSED')"
              class="rounded-lg px-3 py-1 text-xs font-semibold transition-colors"
              [ngClass]="filterStatus() === 'CLOSED' ? 'bg-indigo-600 text-white' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-100'"
            >
              Ciclos Concluídos (Eficaz)
            </button>
          </div>

          <div class="relative min-w-[220px]">
            <input
              type="text"
              [(ngModel)]="searchQuery"
              placeholder="Buscar por área ou plano..."
              class="w-full rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>
      </header>

      <!-- Tabela de Itens do PGR -->
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-200 text-left text-xs">
          <thead class="bg-slate-50 font-semibold text-slate-700">
            <tr>
              <th class="px-5 py-3.5">Área / Equipe</th>
              <th class="px-4 py-3.5">Fator de Risco NR-1</th>
              <th class="px-3 py-3.5 text-center">Nível</th>
              <th class="px-5 py-3.5">Plano de Ação Preventiva</th>
              <th class="px-4 py-3.5">Responsável</th>
              <th class="px-4 py-3.5">Prazo Reavaliação</th>
              <th class="px-4 py-3.5">Status do Ciclo</th>
              <th class="px-4 py-3.5 text-right">Ação SESMT</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 bg-white">
            <tr
              *ngFor="let item of filteredItems()"
              class="hover:bg-slate-50/70 transition-colors"
            >
              <!-- Área -->
              <td class="px-5 py-4 font-bold text-slate-900">
                {{ item.areaName }}
                <div class="text-[10px] font-normal text-slate-400 font-mono">{{ item.itemId }}</div>
              </td>

              <!-- Fator de Risco -->
              <td class="px-4 py-4 text-slate-700">
                <span class="rounded bg-indigo-50 px-2 py-0.5 text-[11px] font-semibold text-indigo-700 border border-indigo-100">
                  {{ formatFactor(item.factor) }}
                </span>
              </td>

              <!-- Nível de Severidade -->
              <td class="px-3 py-4 text-center">
                <span
                  class="inline-block rounded-full px-2.5 py-0.5 text-[10px] font-bold"
                  [ngClass]="{
                    'bg-rose-100 text-rose-800': item.severityLevel === 'VERMELHO',
                    'bg-amber-100 text-amber-800': item.severityLevel === 'AMARELO',
                    'bg-emerald-100 text-emerald-800': item.severityLevel === 'VERDE'
                  }"
                >
                  {{ item.severityLevel }}
                </span>
              </td>

              <!-- Plano de Ação -->
              <td class="px-5 py-4 text-slate-700 max-w-xs">
                <div class="line-clamp-2 hover:line-clamp-none font-medium text-slate-800">
                  {{ item.actionPlanDescription }}
                </div>
                <div class="mt-1 text-[10px] text-slate-400" *ngIf="item.auditLog && item.auditLog.length > 0">
                  Audit: {{ item.auditLog[0] }}
                </div>
              </td>

              <!-- Responsável -->
              <td class="px-4 py-4 text-slate-600 font-medium">
                {{ item.responsiblePerson }}
              </td>

              <!-- Prazo -->
              <td class="px-4 py-4 text-slate-600 font-mono">
                {{ item.deadlineDate }}
                <span class="block text-[10px] text-slate-400">({{ item.reassessmentIntervalDays }} dias)</span>
              </td>

              <!-- Status do Ciclo -->
              <td class="px-4 py-4">
                <span
                  *ngIf="item.closureDate"
                  class="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2.5 py-0.5 text-[10px] font-bold text-emerald-800"
                >
                  <svg class="h-3 w-3 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                  </svg>
                  EFICAZ (ENCERRADO)
                </span>
                <span
                  *ngIf="!item.closureDate"
                  class="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2.5 py-0.5 text-[10px] font-bold text-amber-800 border border-amber-200"
                >
                  <span class="h-1.5 w-1.5 rounded-full bg-amber-500 animate-pulse"></span>
                  EM MONITORAMENTO
                </span>
              </td>

              <!-- Ação SESMT: Reavaliar Eficácia (Cenário 7) -->
              <td class="px-4 py-4 text-right">
                <button
                  *ngIf="!item.closureDate"
                  type="button"
                  (click)="onReavaliar(item)"
                  class="inline-flex items-center gap-1 rounded-lg border border-indigo-200 bg-indigo-50 px-2.5 py-1.5 text-[11px] font-bold text-indigo-700 hover:bg-indigo-100 active:scale-95 transition-all shadow-xs"
                >
                  <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
                  </svg>
                  Reavaliar (60 dias)
                </button>

                <span *ngIf="item.closureDate" class="text-[11px] text-slate-400 font-mono">
                  Auditado em {{ item.closureDate | date:'shortDate' }}
                </span>
              </td>
            </tr>

            <!-- Estado Vazio -->
            <tr *ngIf="filteredItems().length === 0">
              <td colspan="8" class="px-6 py-12 text-center text-slate-400">
                <div class="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 text-slate-400 mb-2">
                  <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                  </svg>
                </div>
                Nenhum item do PGR corresponde aos filtros aplicados.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Modal de Conclusão de Reavaliação de Eficácia (Cenário 7) -->
      <div
        *ngIf="selectedReassessItem()"
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4"
      >
        <div class="w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl border border-slate-200 space-y-4">
          <div class="flex items-center justify-between border-b border-slate-100 pb-3">
            <div class="flex items-center gap-2">
              <div class="flex h-8 w-8 items-center justify-center rounded-xl bg-emerald-600 text-white">
                <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <div>
                <h3 class="text-sm font-bold text-slate-900">
                  Reavaliação de Eficácia de 60 Dias (NR-1)
                </h3>
                <p class="text-[11px] text-slate-500">Área: {{ selectedReassessItem()?.areaName }}</p>
              </div>
            </div>
            <button
              type="button"
              (click)="selectedReassessItem.set(null)"
              class="text-slate-400 hover:text-slate-600"
            >
              <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>

          <!-- Parecer dos Resultados Coletados nos 60 Dias -->
          <div class="rounded-xl border border-emerald-200 bg-emerald-50/70 p-4 space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-emerald-900">Resultado Medido pós Intervenção:</span>
              <span class="rounded bg-emerald-600 px-2 py-0.5 text-xs font-bold text-white font-mono">
                -35% Dias de Atestado
              </span>
            </div>
            <p class="text-xs text-slate-700 leading-relaxed">
              Após a revisão das metas de atendimento pactuada com a liderança e os círculos de escuta do RH, observou-se uma redução de 35% no volume de afastamentos médicos e estabilização de horas extras na área de Atendimento ao Cliente.
            </p>
            <div class="text-[11px] font-semibold text-emerald-800">
              Parecer Técnico: Intervenção Preventiva Homologada como EFICAZ.
            </div>
          </div>

          <div class="flex justify-end gap-2 border-t border-slate-100 pt-3">
            <button
              type="button"
              (click)="selectedReassessItem.set(null)"
              class="rounded-xl px-3.5 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100"
            >
              Cancelar
            </button>
            <button
              type="button"
              (click)="confirmReassessmentClosure()"
              class="rounded-xl bg-emerald-600 px-4 py-2 text-xs font-bold text-white shadow-xs hover:bg-emerald-700 active:scale-95 transition-all"
            >
              Encerrar Ciclo no PGR como Eficaz
            </button>
          </div>
        </div>
      </div>
    </section>
  `,
})
export class PgrInventoryTableComponent {
  @Input() items: PgrInventoryItem[] = [];
  @Output() reassess = new EventEmitter<string>();

  filterStatus = signal<'ALL' | 'OPEN' | 'CLOSED'>('ALL');
  searchQuery = '';
  selectedReassessItem = signal<PgrInventoryItem | null>(null);

  getActiveCount(): number {
    return this.items.filter((i) => !i.closureDate).length;
  }

  filteredItems(): PgrInventoryItem[] {
    return this.items.filter((item) => {
      // Filtro de status
      if (this.filterStatus() === 'OPEN' && item.closureDate) return false;
      if (this.filterStatus() === 'CLOSED' && !item.closureDate) return false;

      // Filtro de busca
      if (this.searchQuery.trim()) {
        const query = this.searchQuery.toLowerCase();
        const matchArea = item.areaName.toLowerCase().includes(query);
        const matchAction = item.actionPlanDescription.toLowerCase().includes(query);
        const matchFactor = item.factor.toLowerCase().includes(query);
        return matchArea || matchAction || matchFactor;
      }
      return true;
    });
  }

  formatFactor(factor: PsychosocialRiskFactor): string {
    const mapa: Record<string, string> = {
      SOBRECARGA_METAS: 'Sobrecarga e Metas',
      LIDERANCA_CONFLITO: 'Conflito com Liderança',
      ASSEDIO: 'Assédio / Risco Grave',
      JORNADAS_LONGAS: 'Jornadas Longas',
      FALTA_CLAREZA_PAPEL: 'Falta de Clareza de Papel',
      FALTA_AUTONOMIA: 'Baixa Autonomia',
      INSEGURANCA_TRABALHO: 'Insegurança no Trabalho',
      ESTAVEL_SEM_FATOR: 'Estável',
    };
    return mapa[factor] || factor;
  }

  onReavaliar(item: PgrInventoryItem): void {
    this.selectedReassessItem.set(item);
  }

  confirmReassessmentClosure(): void {
    const current = this.selectedReassessItem();
    if (current) {
      current.closureDate = new Date().toISOString();
      current.closureNotes = 'Ciclo encerrado com sucesso: redução de 35% nos atestados (Eficaz).';
      current.auditLog.unshift(`Reavaliação 60 dias: Ação concluída com sucesso (Eficaz) em ${new Date().toLocaleDateString('pt-BR')}`);
      this.reassess.emit(current.itemId);
      this.selectedReassessItem.set(null);
    }
  }
}
