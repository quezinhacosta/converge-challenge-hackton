import { Component, Input, Output, EventEmitter, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PgrInventoryItem, PsychosocialRiskFactor } from '../../../../core/models/nr1.model';

@Component({
  selector: 'app-pgr-inventory-table',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="rounded-2xl border border-zinc-700/80 bg-gradient-to-b from-zinc-900/90 to-zinc-950/90 shadow-2xl backdrop-blur-xl overflow-hidden">
      <!-- Cabeçalho Executivo do PGR -->
      <header class="border-b border-zinc-800/80 bg-zinc-950/80 p-7">
        <div class="flex flex-wrap items-center justify-between gap-5">
          <div>
            <div class="flex items-center gap-2.5">
              <span class="rounded-lg bg-violet-950/60 px-3 py-1 text-xs font-mono font-bold text-violet-300 border border-violet-800/60 shadow-sm">
                PGR &bull; NR-1 Oficial
              </span>
              <span class="text-xs text-zinc-300 font-mono font-medium">Portaria MTE nº 1.419/2024</span>
            </div>
            <h2 class="mt-2 text-xl font-black text-white tracking-tight flex items-center gap-2.5">
              <span>Inventário Oficial de Riscos Psicossociais & Plano de Ação</span>
            </h2>
            <p class="text-sm text-zinc-300 font-medium mt-1">
              Registros auditáveis com cronograma, responsáveis e ciclos de reavaliação de eficácia (60 dias).
            </p>
          </div>

          <div class="flex items-center gap-3">
            <button
              type="button"
              (click)="exportarDossiePdf()"
              class="inline-flex items-center gap-2 rounded-xl border border-zinc-700 bg-zinc-800/90 hover:bg-zinc-700 hover:border-zinc-600 px-4 py-2.5 text-xs font-bold text-zinc-100 shadow-md transition-all hover:scale-[1.02] active:scale-95"
            >
              <svg class="h-4 w-4 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
              Exportar Dossiê (PDF)
            </button>

            <span class="inline-flex items-center gap-2 rounded-xl bg-zinc-900 border border-zinc-700 px-3.5 py-2 text-xs font-mono font-bold text-zinc-200 shadow-inner">
              <span class="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
              {{ getActiveCount() }} Planos Ativos
            </span>
          </div>
        </div>

        <!-- Filtros e Busca -->
        <div class="mt-5 flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-zinc-800/80">
          <div class="flex items-center gap-2">
            <button
              type="button"
              (click)="filterStatus.set('ALL')"
              class="rounded-lg px-3.5 py-1.5 text-xs font-bold transition-all shadow-sm"
              [ngClass]="filterStatus() === 'ALL' ? 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white border border-violet-400/40' : 'bg-zinc-900 border border-zinc-800 text-zinc-300 hover:text-white'"
            >
              Todos ({{ items.length }})
            </button>
            <button
              type="button"
              (click)="filterStatus.set('OPEN')"
              class="rounded-lg px-3.5 py-1.5 text-xs font-bold transition-all shadow-sm"
              [ngClass]="filterStatus() === 'OPEN' ? 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white border border-violet-400/40' : 'bg-zinc-900 border border-zinc-800 text-zinc-300 hover:text-white'"
            >
              Em Acompanhamento
            </button>
            <button
              type="button"
              (click)="filterStatus.set('CLOSED')"
              class="rounded-lg px-3.5 py-1.5 text-xs font-bold transition-all shadow-sm"
              [ngClass]="filterStatus() === 'CLOSED' ? 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white border border-violet-400/40' : 'bg-zinc-900 border border-zinc-800 text-zinc-300 hover:text-white'"
            >
              Ciclos Concluídos (Eficaz)
            </button>
          </div>

          <div class="relative min-w-[260px]">
            <input
              type="text"
              [(ngModel)]="searchQuery"
              placeholder="Buscar por setor ou plano..."
              class="w-full rounded-xl border border-zinc-700 bg-zinc-900/90 px-3.5 py-2 text-xs text-zinc-100 placeholder-zinc-400 focus:outline-none focus:border-violet-500 shadow-inner"
            />
          </div>
        </div>
      </header>

      <!-- Tabela com Tipografia Clara e Espaçamento Confortável -->
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-zinc-800 text-left text-sm">
          <thead class="bg-zinc-950 font-bold text-zinc-300">
            <tr>
              <th class="px-5 py-4 font-mono uppercase tracking-wider text-xs">Área / Setor</th>
              <th class="px-4 py-4 font-mono uppercase tracking-wider text-xs">Fator NR-1</th>
              <th class="px-3 py-4 text-center font-mono uppercase tracking-wider text-xs">Nível</th>
              <th class="px-5 py-4 font-mono uppercase tracking-wider text-xs">Plano de Ação Homologado</th>
              <th class="px-4 py-4 font-mono uppercase tracking-wider text-xs">Responsável</th>
              <th class="px-4 py-4 font-mono uppercase tracking-wider text-xs">Prazo</th>
              <th class="px-4 py-4 font-mono uppercase tracking-wider text-xs">Status Ciclo</th>
              <th class="px-5 py-4 text-right font-mono uppercase tracking-wider text-xs">Ação SESMT</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-zinc-800/70 bg-zinc-950/30">
            <tr
              *ngFor="let item of filteredItems()"
              class="hover:bg-zinc-900/60 transition-colors"
            >
              <!-- Área -->
              <td class="px-5 py-4 font-bold text-white">
                {{ item.areaName }}
                <div class="text-xs text-zinc-400 font-mono font-normal">{{ item.itemId }}</div>
              </td>

              <!-- Fator -->
              <td class="px-4 py-4 text-zinc-200">
                <span class="rounded-lg bg-zinc-800/90 px-2.5 py-1 text-xs font-semibold text-zinc-200 border border-zinc-700">
                  {{ formatFactor(item.factor) }}
                </span>
              </td>

              <!-- Nível de Severidade -->
              <td class="px-3 py-4 text-center">
                <span
                  class="inline-block rounded-md px-3 py-1 text-xs font-black shadow-sm"
                  [ngClass]="{
                    'bg-rose-950/70 text-rose-300 border border-rose-700/60': item.severityLevel === 'VERMELHO',
                    'bg-amber-950/70 text-amber-300 border border-amber-700/60': item.severityLevel === 'AMARELO',
                    'bg-emerald-950/70 text-emerald-300 border border-emerald-700/60': item.severityLevel === 'VERDE'
                  }"
                >
                  {{ item.severityLevel }}
                </span>
              </td>

              <!-- Plano de Ação -->
              <td class="px-5 py-4 text-zinc-200 max-w-sm">
                <div class="font-medium text-white leading-relaxed">
                  {{ item.actionPlanDescription }}
                </div>
                <div class="mt-1 text-xs text-zinc-400 font-mono" *ngIf="item.auditLog && item.auditLog.length > 0">
                  Auditoria: {{ item.auditLog[0] }}
                </div>
              </td>

              <!-- Responsável -->
              <td class="px-4 py-4 text-zinc-200 font-medium">
                {{ item.responsiblePerson }}
              </td>

              <!-- Prazo -->
              <td class="px-4 py-4 text-zinc-200 font-mono font-medium">
                {{ item.deadlineDate }}
                <span class="block text-xs text-zinc-400 font-mono">({{ item.reassessmentIntervalDays }} dias)</span>
              </td>

              <!-- Status do Ciclo -->
              <td class="px-4 py-4">
                <span
                  *ngIf="item.closureDate"
                  class="inline-flex items-center gap-1.5 rounded-lg bg-emerald-950/60 px-3 py-1 text-xs font-mono font-bold text-emerald-300 border border-emerald-800/60 shadow-sm"
                >
                  <svg class="h-3.5 w-3.5 text-emerald-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                  </svg>
                  EFICAZ (ENCERRADO)
                </span>
                <span
                  *ngIf="!item.closureDate"
                  class="inline-flex items-center gap-1.5 rounded-lg bg-amber-950/50 px-3 py-1 text-xs font-mono font-bold text-amber-300 border border-amber-800/60"
                >
                  <span class="h-1.5 w-1.5 rounded-full bg-amber-400 animate-pulse"></span>
                  MONITORAMENTO ATIVO
                </span>
              </td>

              <!-- Ação SESMT -->
              <td class="px-5 py-4 text-right">
                <button
                  *ngIf="!item.closureDate"
                  type="button"
                  (click)="onReassessClick(item)"
                  class="inline-flex items-center gap-1.5 rounded-lg border border-zinc-700 bg-zinc-800/90 hover:bg-zinc-700 hover:border-zinc-500 px-3 py-1.5 text-xs font-bold text-zinc-100 transition-all shadow-sm hover:scale-105 active:scale-95"
                >
                  <svg class="h-3.5 w-3.5 text-teal-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                  </svg>
                  Reavaliar (60d)
                </button>
                <span *ngIf="item.closureDate" class="text-xs text-zinc-400 font-mono font-bold">
                  Concluído
                </span>
              </td>
            </tr>

            <tr *ngIf="filteredItems().length === 0">
              <td colspan="8" class="px-6 py-8 text-center text-zinc-400 font-medium">
                Nenhum registro encontrado para o filtro aplicado.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Modal de Reavaliação de Eficácia de 60 Dias -->
      <div
        *ngIf="selectedItemForReassessment()"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-fadeIn"
      >
        <div class="w-full max-w-lg rounded-2xl border border-zinc-700 bg-zinc-900 p-7 space-y-5 shadow-2xl">
          <div class="flex items-start justify-between border-b border-zinc-800 pb-4">
            <div>
              <span class="rounded-md bg-emerald-950/60 px-2.5 py-0.5 text-xs font-mono font-bold text-emerald-300 border border-emerald-800/60">
                Caso 7: Fechamento de Ciclo (60 dias)
              </span>
              <h3 class="text-lg font-black text-white mt-1.5">
                Reavaliação Formal de Eficácia &bull; {{ selectedItemForReassessment()!.areaName }}
              </h3>
            </div>
            <button
              type="button"
              (click)="selectedItemForReassessment.set(null)"
              class="text-zinc-400 hover:text-white text-xl font-bold"
            >
              &times;
            </button>
          </div>

          <div class="rounded-xl border border-zinc-800 bg-zinc-950 p-5 space-y-3 text-sm">
            <h5 class="font-bold text-zinc-200">
              Indicadores Observados após a Intervenção:
            </h5>
            <div class="grid grid-cols-2 gap-4 pt-1">
              <div class="bg-zinc-900/80 p-4 rounded-xl border border-zinc-800">
                <span class="text-zinc-300 font-medium text-xs">Dias de Atestado:</span>
                <div class="text-2xl font-black font-mono text-emerald-400 mt-1">-38.5%</div>
                <span class="text-xs text-zinc-400 font-mono">queda expressiva</span>
              </div>
              <div class="bg-zinc-900/80 p-4 rounded-xl border border-zinc-800">
                <span class="text-zinc-300 font-medium text-xs">Pesquisa Pulso:</span>
                <div class="text-2xl font-black font-mono text-emerald-400 mt-1">3.8 / 5.0</div>
                <span class="text-xs text-zinc-400 font-mono">recuperação do clima</span>
              </div>
            </div>
            <p class="text-zinc-200 pt-2 leading-relaxed font-medium">
              O motor vitAI validou a eficácia da medida preventiva adotada (revisão de metas e escuta ativa).
              O risco no setor de Atendimento ao Cliente recuou de <strong>Vermelho</strong> para <strong>Verde</strong>.
            </p>
          </div>

          <div class="flex justify-end gap-3 pt-3 border-t border-zinc-800">
            <button
              type="button"
              (click)="selectedItemForReassessment.set(null)"
              class="rounded-xl border border-zinc-700 bg-zinc-800 hover:bg-zinc-700 px-4 py-2 text-xs font-bold text-zinc-300 transition-all"
            >
              Cancelar
            </button>
            <button
              type="button"
              (click)="confirmReassessment()"
              class="rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 px-5 py-2 text-xs font-bold text-white transition-all shadow-lg shadow-emerald-950/60"
            >
              Homologar Eficácia e Encerrar Risco no PGR
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
  selectedItemForReassessment = signal<PgrInventoryItem | null>(null);

  getActiveCount(): number {
    return this.items.filter((i) => !i.closureDate).length;
  }

  filteredItems(): PgrInventoryItem[] {
    return this.items.filter((item) => {
      const matchesFilter =
        this.filterStatus() === 'ALL' ||
        (this.filterStatus() === 'OPEN' && !item.closureDate) ||
        (this.filterStatus() === 'CLOSED' && !!item.closureDate);

      const query = this.searchQuery.toLowerCase().trim();
      const matchesSearch =
        !query ||
        item.areaName.toLowerCase().includes(query) ||
        item.actionPlanDescription.toLowerCase().includes(query) ||
        item.responsiblePerson.toLowerCase().includes(query);

      return matchesFilter && matchesSearch;
    });
  }

  formatFactor(factor: PsychosocialRiskFactor | string): string {
    const map: Record<string, string> = {
      SOBRECARGA_METAS: 'Sobrecarga de Metas',
      LIDERANCA_CONFLITO: 'Gestão e Conflitos',
      ASSEDIO: 'Assédio / Ética',
      JORNADA_EXCESSIVA: 'Jornada Excessiva',
      OUTRO: 'Geral',
    };
    return map[factor] || factor;
  }

  onReassessClick(item: PgrInventoryItem): void {
    this.selectedItemForReassessment.set(item);
  }

  confirmReassessment(): void {
    const item = this.selectedItemForReassessment();
    if (!item) return;
    this.selectedItemForReassessment.set(null);
    this.reassess.emit(item.itemId);
  }

  exportarDossiePdf(): void {
    window.print();
  }
}
