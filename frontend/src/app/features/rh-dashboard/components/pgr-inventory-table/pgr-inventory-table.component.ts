import { Component, Input, Output, EventEmitter, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PgrInventoryItem, PsychosocialRiskFactor } from '../../../../core/models/nr1.model';

@Component({
  selector: 'app-pgr-inventory-table',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="rounded-xl border border-zinc-800 bg-zinc-900/30 overflow-hidden">
      <!-- Cabeçalho Executivo do PGR -->
      <header class="border-b border-zinc-800/80 bg-zinc-950/70 p-5">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div class="flex items-center gap-2">
              <span class="rounded bg-zinc-800 px-2 py-0.5 text-[11px] font-mono text-zinc-300 border border-zinc-700">
                PGR &bull; NR-1
              </span>
              <span class="text-xs text-zinc-400 font-mono">Portaria MTE nº 1.419/2024</span>
            </div>
            <h2 class="mt-1 text-base font-semibold text-white">
              Inventário Oficial de Riscos Psicossociais & Plano de Ação
            </h2>
            <p class="text-xs text-zinc-400 mt-0.5">
              Registros auditáveis com cronograma, responsáveis e ciclos de reavaliação de 60 dias.
            </p>
          </div>

          <div class="flex items-center gap-2">
            <button
              type="button"
              (click)="exportarDossiePdf()"
              class="inline-flex items-center gap-1.5 rounded-lg border border-zinc-700 bg-zinc-800 hover:bg-zinc-700 px-3 py-1.5 text-xs font-medium text-zinc-200 transition-colors"
            >
              <svg class="h-3.5 w-3.5 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
              Exportar Dossiê (PDF)
            </button>

            <span class="inline-flex items-center gap-1.5 rounded-lg bg-zinc-900 px-2.5 py-1.5 text-xs font-mono text-zinc-300 border border-zinc-800">
              <span class="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
              {{ getActiveCount() }} Planos em Execução
            </span>
          </div>
        </div>

        <!-- Filtros e Busca -->
        <div class="mt-4 flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-zinc-800/60">
          <div class="flex items-center gap-1.5">
            <button
              type="button"
              (click)="filterStatus.set('ALL')"
              class="rounded-md px-2.5 py-1 text-xs font-medium transition-colors"
              [ngClass]="filterStatus() === 'ALL' ? 'bg-zinc-800 text-white font-semibold border border-zinc-700' : 'bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-zinc-200'"
            >
              Todos ({{ items.length }})
            </button>
            <button
              type="button"
              (click)="filterStatus.set('OPEN')"
              class="rounded-md px-2.5 py-1 text-xs font-medium transition-colors"
              [ngClass]="filterStatus() === 'OPEN' ? 'bg-zinc-800 text-white font-semibold border border-zinc-700' : 'bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-zinc-200'"
            >
              Em Acompanhamento
            </button>
            <button
              type="button"
              (click)="filterStatus.set('CLOSED')"
              class="rounded-md px-2.5 py-1 text-xs font-medium transition-colors"
              [ngClass]="filterStatus() === 'CLOSED' ? 'bg-zinc-800 text-white font-semibold border border-zinc-700' : 'bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-zinc-200'"
            >
              Ciclos Concluídos (Eficaz)
            </button>
          </div>

          <div class="relative min-w-[220px]">
            <input
              type="text"
              [(ngModel)]="searchQuery"
              placeholder="Buscar por setor ou plano..."
              class="w-full rounded-md border border-zinc-800 bg-zinc-900 px-3 py-1 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600"
            />
          </div>
        </div>
      </header>

      <!-- Tabela -->
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-zinc-800 text-left text-xs">
          <thead class="bg-zinc-950 font-medium text-zinc-400">
            <tr>
              <th class="px-4 py-3 font-mono uppercase tracking-wider text-[11px]">Área / Setor</th>
              <th class="px-3 py-3 font-mono uppercase tracking-wider text-[11px]">Fator NR-1</th>
              <th class="px-3 py-3 text-center font-mono uppercase tracking-wider text-[11px]">Nível</th>
              <th class="px-4 py-3 font-mono uppercase tracking-wider text-[11px]">Plano de Ação Homologado</th>
              <th class="px-3 py-3 font-mono uppercase tracking-wider text-[11px]">Responsável</th>
              <th class="px-3 py-3 font-mono uppercase tracking-wider text-[11px]">Prazo</th>
              <th class="px-3 py-3 font-mono uppercase tracking-wider text-[11px]">Status Ciclo</th>
              <th class="px-4 py-3 text-right font-mono uppercase tracking-wider text-[11px]">Ação SESMT</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-zinc-800/60 bg-zinc-950/20">
            <tr
              *ngFor="let item of filteredItems()"
              class="hover:bg-zinc-900/40 transition-colors"
            >
              <!-- Área -->
              <td class="px-4 py-3.5 font-medium text-white">
                {{ item.areaName }}
                <div class="text-[10px] text-zinc-500 font-mono">{{ item.itemId }}</div>
              </td>

              <!-- Fator -->
              <td class="px-3 py-3.5 text-zinc-300">
                <span class="rounded bg-zinc-800/80 px-2 py-0.5 text-[11px] font-medium text-zinc-300 border border-zinc-700/60">
                  {{ formatFactor(item.factor) }}
                </span>
              </td>

              <!-- Nível de Severidade -->
              <td class="px-3 py-3.5 text-center">
                <span
                  class="inline-block rounded px-2 py-0.5 text-[10px] font-bold"
                  [ngClass]="{
                    'bg-rose-950/40 text-rose-300 border border-rose-800/40': item.severityLevel === 'VERMELHO',
                    'bg-amber-950/40 text-amber-300 border border-amber-800/40': item.severityLevel === 'AMARELO',
                    'bg-emerald-950/40 text-emerald-300 border border-emerald-800/40': item.severityLevel === 'VERDE'
                  }"
                >
                  {{ item.severityLevel }}
                </span>
              </td>

              <!-- Plano de Ação -->
              <td class="px-4 py-3.5 text-zinc-300 max-w-xs">
                <div class="line-clamp-2 hover:line-clamp-none font-medium text-zinc-200">
                  {{ item.actionPlanDescription }}
                </div>
                <div class="mt-0.5 text-[10px] text-zinc-500 font-mono" *ngIf="item.auditLog && item.auditLog.length > 0">
                  Auditoria: {{ item.auditLog[0] }}
                </div>
              </td>

              <!-- Responsável -->
              <td class="px-3 py-3.5 text-zinc-300">
                {{ item.responsiblePerson }}
              </td>

              <!-- Prazo -->
              <td class="px-3 py-3.5 text-zinc-300 font-mono">
                {{ item.deadlineDate }}
                <span class="block text-[10px] text-zinc-500 font-mono">({{ item.reassessmentIntervalDays }} dias)</span>
              </td>

              <!-- Status do Ciclo -->
              <td class="px-3 py-3.5">
                <span
                  *ngIf="item.closureDate"
                  class="inline-flex items-center gap-1 rounded bg-emerald-950/30 px-2 py-0.5 text-[10px] font-mono font-medium text-emerald-400 border border-emerald-800/40"
                >
                  EFICAZ (ENCERRADO)
                </span>
                <span
                  *ngIf="!item.closureDate"
                  class="inline-flex items-center gap-1 rounded bg-amber-950/30 px-2 py-0.5 text-[10px] font-mono font-medium text-amber-300 border border-amber-800/40"
                >
                  MONITORAMENTO ATIVO
                </span>
              </td>

              <!-- Ação SESMT -->
              <td class="px-4 py-3.5 text-right">
                <button
                  *ngIf="!item.closureDate"
                  type="button"
                  (click)="onReassessClick(item)"
                  class="inline-flex items-center gap-1 rounded border border-zinc-700 bg-zinc-800 hover:bg-zinc-700 px-2.5 py-1 text-[11px] font-medium text-zinc-200 transition-colors"
                >
                  Reavaliar (60d)
                </button>
                <span *ngIf="item.closureDate" class="text-[11px] text-zinc-500 font-mono">
                  Concluído
                </span>
              </td>
            </tr>

            <tr *ngIf="filteredItems().length === 0">
              <td colspan="8" class="px-6 py-6 text-center text-zinc-500">
                Nenhum registro encontrado para o filtro aplicado.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Modal de Reavaliação de Eficácia de 60 Dias -->
      <div
        *ngIf="selectedItemForReassessment()"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-xs p-4"
      >
        <div class="w-full max-w-lg rounded-xl border border-zinc-800 bg-zinc-900 p-6 space-y-4">
          <div class="flex items-start justify-between border-b border-zinc-800 pb-3">
            <div>
              <span class="text-[11px] font-mono text-zinc-400">
                Caso 7: Fechamento de Ciclo (60 dias)
              </span>
              <h3 class="text-base font-semibold text-white mt-0.5">
                Reavaliação Formal de Eficácia &bull; {{ selectedItemForReassessment()!.areaName }}
              </h3>
            </div>
            <button
              type="button"
              (click)="selectedItemForReassessment.set(null)"
              class="text-zinc-400 hover:text-white text-base"
            >
              &times;
            </button>
          </div>

          <div class="rounded-lg border border-zinc-800 bg-zinc-950 p-4 space-y-2 text-xs">
            <h5 class="font-medium text-zinc-300">
              Indicadores Observados após a Intervenção:
            </h5>
            <div class="grid grid-cols-2 gap-3 pt-1">
              <div class="bg-zinc-900/60 p-3 rounded-md border border-zinc-800">
                <span class="text-zinc-400">Dias de Atestado:</span>
                <div class="text-base font-bold font-mono text-emerald-400 mt-0.5">-38.5%</div>
                <span class="text-[10px] text-zinc-500 font-mono">queda significativa</span>
              </div>
              <div class="bg-zinc-900/60 p-3 rounded-md border border-zinc-800">
                <span class="text-zinc-400">Pesquisa Pulso:</span>
                <div class="text-base font-bold font-mono text-emerald-400 mt-0.5">3.8 / 5.0</div>
                <span class="text-[10px] text-zinc-500 font-mono">recuperação do clima</span>
              </div>
            </div>
            <p class="text-zinc-300 pt-2 leading-relaxed">
              O motor vitAI validou a eficácia da medida preventiva adotada (revisão de metas e escuta ativa).
              O risco no setor de Atendimento ao Cliente recuou de <strong>Vermelho</strong> para <strong>Verde</strong>.
            </p>
          </div>

          <div class="flex justify-end gap-2 pt-2 border-t border-zinc-800">
            <button
              type="button"
              (click)="selectedItemForReassessment.set(null)"
              class="rounded-lg border border-zinc-700 bg-zinc-800 hover:bg-zinc-700 px-3.5 py-1.5 text-xs font-medium text-zinc-300"
            >
              Cancelar
            </button>
            <button
              type="button"
              (click)="confirmReassessment()"
              class="rounded-lg bg-emerald-600 hover:bg-emerald-500 px-3.5 py-1.5 text-xs font-medium text-white transition-colors"
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
