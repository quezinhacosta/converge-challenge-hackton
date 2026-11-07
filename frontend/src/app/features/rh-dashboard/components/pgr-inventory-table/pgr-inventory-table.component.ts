import { Component, Input, Output, EventEmitter, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PgrInventoryItem, RiskLevel, PsychosocialRiskFactor } from '../../../../core/models/nr1.model';

@Component({
  selector: 'app-pgr-inventory-table',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="overflow-hidden rounded-2xl border border-zinc-800 bg-[#121118]/90 backdrop-blur-md shadow-glass">
      <!-- Cabeçalho Executivo do PGR -->
      <header class="border-b border-zinc-800/80 bg-zinc-900/60 p-6">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div class="flex items-center gap-2">
              <span class="inline-flex items-center gap-1.5 rounded-lg bg-violet-950/50 px-2.5 py-0.5 text-xs font-mono font-bold text-violet-300 border border-violet-800/50">
                <span class="h-1.5 w-1.5 rounded-full bg-[#8B5CF6] shadow-[0_0_6px_#8B5CF6]"></span>
                PGR &bull; Programa de Gerenciamento de Riscos
              </span>
              <span class="text-xs text-zinc-400 font-mono">Portaria MTE nº 1.419/2024</span>
            </div>
            <h2 class="mt-1.5 text-xl font-bold tracking-tight text-white flex items-center gap-2">
              Inventário Oficial de Riscos Psicossociais & Plano de Ação
            </h2>
            <p class="text-xs text-zinc-400 mt-0.5">
              Registros auditáveis com cronograma, responsáveis e ciclos de reavaliação de eficácia (60 dias).
            </p>
          </div>

          <div class="flex items-center gap-2.5">
            <button
              type="button"
              (click)="exportarDossiePdf()"
              class="inline-flex items-center gap-1.5 rounded-xl border border-zinc-700 bg-zinc-900/90 px-3.5 py-2 text-xs font-bold text-zinc-200 hover:border-violet-500 hover:text-white transition-all shadow-xs"
            >
              <svg class="h-4 w-4 text-[#8B5CF6]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
              [ Exportar Dossiê PGR (PDF) ]
            </button>

            <span class="inline-flex items-center gap-1.5 rounded-xl bg-zinc-900 px-3 py-2 text-xs font-mono font-bold text-[#CCFF00] border border-zinc-800">
              <span class="h-2 w-2 rounded-full bg-[#CCFF00] shadow-[0_0_8px_#CCFF00]"></span>
              {{ getActiveCount() }} Ações Ativas
            </span>
          </div>
        </div>

        <!-- Barra de Filtros e Busca -->
        <div class="mt-4 flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-zinc-800/60">
          <div class="flex items-center gap-2">
            <button
              type="button"
              (click)="filterStatus.set('ALL')"
              class="rounded-lg px-3 py-1 text-xs font-semibold transition-all"
              [ngClass]="filterStatus() === 'ALL' ? 'bg-[#7C3AED] text-white shadow-[0_0_12px_rgba(124,58,237,0.35)]' : 'bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-white'"
            >
              Todos ({{ items.length }})
            </button>
            <button
              type="button"
              (click)="filterStatus.set('OPEN')"
              class="rounded-lg px-3 py-1 text-xs font-semibold transition-all"
              [ngClass]="filterStatus() === 'OPEN' ? 'bg-[#7C3AED] text-white shadow-[0_0_12px_rgba(124,58,237,0.35)]' : 'bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-white'"
            >
              Em Acompanhamento
            </button>
            <button
              type="button"
              (click)="filterStatus.set('CLOSED')"
              class="rounded-lg px-3 py-1 text-xs font-semibold transition-all"
              [ngClass]="filterStatus() === 'CLOSED' ? 'bg-[#7C3AED] text-white shadow-[0_0_12px_rgba(124,58,237,0.35)]' : 'bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-white'"
            >
              Ciclos Concluídos (Eficaz)
            </button>
          </div>

          <div class="relative min-w-[240px]">
            <input
              type="text"
              [(ngModel)]="searchQuery"
              placeholder="Buscar por área ou plano..."
              class="w-full rounded-lg border border-zinc-800 bg-zinc-900/90 px-3 py-1.5 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-violet-500"
            />
          </div>
        </div>
      </header>

      <!-- Tabela de Itens do PGR -->
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-zinc-800 text-left text-xs">
          <thead class="bg-zinc-950 font-semibold text-zinc-400">
            <tr>
              <th class="px-5 py-3.5 font-mono uppercase tracking-wider text-[11px]">Área / Setor</th>
              <th class="px-4 py-3.5 font-mono uppercase tracking-wider text-[11px]">Fator NR-1</th>
              <th class="px-3 py-3.5 text-center font-mono uppercase tracking-wider text-[11px]">Nível</th>
              <th class="px-5 py-3.5 font-mono uppercase tracking-wider text-[11px]">Plano de Ação Homologado</th>
              <th class="px-4 py-3.5 font-mono uppercase tracking-wider text-[11px]">Responsável</th>
              <th class="px-4 py-3.5 font-mono uppercase tracking-wider text-[11px]">Prazo Reavaliação</th>
              <th class="px-4 py-3.5 font-mono uppercase tracking-wider text-[11px]">Status Ciclo</th>
              <th class="px-4 py-3.5 text-right font-mono uppercase tracking-wider text-[11px]">Ação SESMT</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-zinc-800/80 bg-[#121118]/60">
            <tr
              *ngFor="let item of filteredItems()"
              class="hover:bg-zinc-900/80 transition-colors"
            >
              <!-- Área -->
              <td class="px-5 py-4 font-bold text-white">
                {{ item.areaName }}
                <div class="text-[10px] font-normal text-zinc-500 font-mono">{{ item.itemId }}</div>
              </td>

              <!-- Fator de Risco -->
              <td class="px-4 py-4 text-zinc-300">
                <span class="rounded bg-violet-950/60 px-2 py-0.5 text-[11px] font-medium text-violet-300 border border-violet-800/40">
                  {{ formatFactor(item.factor) }}
                </span>
              </td>

              <!-- Nível de Severidade -->
              <td class="px-3 py-4 text-center">
                <span
                  class="inline-block rounded-full px-2.5 py-0.5 text-[10px] font-bold"
                  [ngClass]="{
                    'bg-rose-950/60 text-rose-400 border border-rose-800/50 shadow-[0_0_8px_rgba(244,63,94,0.2)]': item.severityLevel === 'VERMELHO',
                    'bg-amber-950/60 text-amber-300 border border-amber-800/50': item.severityLevel === 'AMARELO',
                    'bg-emerald-950/60 text-[#CCFF00] border border-emerald-800/50': item.severityLevel === 'VERDE'
                  }"
                >
                  {{ item.severityLevel }}
                </span>
              </td>

              <!-- Plano de Ação -->
              <td class="px-5 py-4 text-zinc-300 max-w-xs">
                <div class="line-clamp-2 hover:line-clamp-none font-medium text-zinc-200">
                  {{ item.actionPlanDescription }}
                </div>
                <div class="mt-1 text-[10px] text-zinc-500 font-mono" *ngIf="item.auditLog && item.auditLog.length > 0">
                  Audit: {{ item.auditLog[0] }}
                </div>
              </td>

              <!-- Responsável -->
              <td class="px-4 py-4 text-zinc-300 font-medium">
                {{ item.responsiblePerson }}
              </td>

              <!-- Prazo -->
              <td class="px-4 py-4 text-zinc-300 font-mono">
                {{ item.deadlineDate }}
                <span class="block text-[10px] text-zinc-500 font-mono">({{ item.reassessmentIntervalDays }} dias)</span>
              </td>

              <!-- Status do Ciclo -->
              <td class="px-4 py-4">
                <span
                  *ngIf="item.closureDate"
                  class="inline-flex items-center gap-1.5 rounded-full bg-emerald-950/60 px-2.5 py-0.5 text-[10px] font-mono font-bold text-[#CCFF00] border border-emerald-800/60 shadow-[0_0_10px_rgba(204,255,0,0.2)]"
                >
                  <svg class="h-3 w-3 text-[#CCFF00]" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                  </svg>
                  EFICAZ (ENCERRADO)
                </span>
                <span
                  *ngIf="!item.closureDate"
                  class="inline-flex items-center gap-1.5 rounded-full bg-amber-950/40 px-2.5 py-0.5 text-[10px] font-mono font-bold text-amber-300 border border-amber-800/50"
                >
                  <span class="h-1.5 w-1.5 rounded-full bg-amber-400 animate-pulse"></span>
                  MONITORAMENTO ATIVO
                </span>
              </td>

              <!-- Ação SESMT: Reavaliar Eficácia -->
              <td class="px-4 py-4 text-right">
                <button
                  *ngIf="!item.closureDate"
                  type="button"
                  (click)="onReassessClick(item)"
                  class="inline-flex items-center gap-1 rounded-lg bg-zinc-900 border border-zinc-700 px-3 py-1.5 text-[11px] font-bold text-zinc-200 hover:border-[#CCFF00] hover:text-[#CCFF00] transition-all shadow-xs"
                  title="Simular Reavaliação de 60 dias (Caso 7)"
                >
                  <svg class="h-3.5 w-3.5 text-[#CCFF00]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                  </svg>
                  Reavaliar (60d)
                </button>
                <span *ngIf="item.closureDate" class="text-[11px] text-zinc-500 font-mono">
                  Concluído
                </span>
              </td>
            </tr>

            <tr *ngIf="filteredItems().length === 0">
              <td colspan="8" class="px-6 py-8 text-center text-zinc-500">
                Nenhum registro encontrado para o filtro aplicado.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Modal de Reavaliação de Eficácia de 60 Dias (Caso 7) -->
      <div
        *ngIf="selectedItemForReassessment()"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-fadeIn"
      >
        <div class="w-full max-w-lg rounded-2xl border border-violet-800/60 bg-[#121118] p-6 shadow-2xl space-y-4">
          <div class="flex items-start justify-between border-b border-zinc-800 pb-3">
            <div>
              <span class="inline-flex items-center gap-1 rounded-md bg-emerald-950/60 px-2 py-0.5 text-[11px] font-mono font-bold text-[#CCFF00] border border-emerald-800/40">
                Caso 7: Fechamento de Ciclo (60 dias)
              </span>
              <h3 class="text-lg font-bold text-white mt-1">
                Reavaliação Formal de Eficácia &bull; {{ selectedItemForReassessment()!.areaName }}
              </h3>
            </div>
            <button
              type="button"
              (click)="selectedItemForReassessment.set(null)"
              class="text-zinc-400 hover:text-white text-lg font-bold"
            >
              &times;
            </button>
          </div>

          <div class="rounded-xl border border-zinc-800 bg-zinc-900/80 p-4 space-y-2 text-xs">
            <h5 class="font-bold uppercase tracking-wider text-violet-300 font-mono">
              Indicadores Observados após a Intervenção:
            </h5>
            <div class="grid grid-cols-2 gap-3 pt-1">
              <div class="bg-zinc-950 p-3 rounded-lg border border-zinc-800">
                <span class="text-zinc-400">Dias de Atestado:</span>
                <div class="text-lg font-bold font-mono text-[#CCFF00] mt-0.5">-38.5%</div>
                <span class="text-[10px] text-zinc-500 font-mono">redução acentuada</span>
              </div>
              <div class="bg-zinc-950 p-3 rounded-lg border border-zinc-800">
                <span class="text-zinc-400">Pesquisa Pulso:</span>
                <div class="text-lg font-bold font-mono text-[#CCFF00] mt-0.5">3.8 / 5.0</div>
                <span class="text-[10px] text-zinc-500 font-mono">recuperação do clima</span>
              </div>
            </div>
            <p class="text-zinc-300 pt-2 leading-relaxed">
              O Digital Worker VYTAL.ai detectou eficácia da medida preventiva adotada (revisão de metas e escuta ativa).
              O risco no setor de Atendimento ao Cliente recuou de <strong>Vermelho</strong> para <strong>Verde</strong>.
            </p>
          </div>

          <div class="flex justify-end gap-2.5 pt-2 border-t border-zinc-800">
            <button
              type="button"
              (click)="selectedItemForReassessment.set(null)"
              class="rounded-xl border border-zinc-700 bg-zinc-900 px-4 py-2 text-xs font-bold text-zinc-300 hover:text-white"
            >
              Cancelar
            </button>
            <button
              type="button"
              (click)="confirmReassessment()"
              class="rounded-xl bg-[#CCFF00] px-4 py-2 text-xs font-black text-black hover:bg-[#b8e600] shadow-[0_0_15px_rgba(204,255,0,0.3)]"
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
