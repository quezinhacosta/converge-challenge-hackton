import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AreaHistoryComparison } from '../../../../core/models/signals.model';

@Component({
  selector: 'app-area-signals-view',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div *ngIf="comparison" class="space-y-4">
      <!-- Caso A: Área com menos de 5 pessoas (Quórum insuficiente - Proteção LGPD por exclusão) -->
      <section
        *ngIf="comparison.isAnonymized || comparison.headcount < 5"
        class="rounded-xl border border-zinc-800 bg-zinc-950 p-6"
      >
        <div class="flex items-start gap-4">
          <!-- Ícone de Proteção -->
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-300">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
          </div>

          <div class="flex-1 space-y-2">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <span class="inline-flex items-center gap-1.5 rounded-md bg-zinc-900 border border-zinc-700 px-2.5 py-0.5 text-xs font-mono font-medium text-zinc-200">
                Proteção de Privacidade LGPD (N &lt; 5) &bull; Bloqueio Ativo
              </span>
              <span class="text-xs font-mono text-zinc-400">Headcount = {{ comparison.headcount }} pessoas</span>
            </div>

            <h3 class="text-base font-semibold text-white flex items-center gap-2">
              Área: {{ comparison.areaName }}
              <span class="text-xs font-mono font-normal text-zinc-400 bg-zinc-900 px-2 py-0.5 rounded border border-zinc-800">
                Dados Agregados Ocultados
              </span>
            </h3>

            <p class="text-xs text-zinc-300 leading-relaxed">
              Esta equipe possui <strong>{{ comparison.headcount }} colaboradores</strong> (quórum inferior ao limite mínimo de <strong>5 pessoas</strong> exigido para análises coletivas).
              Para impedir a identificação indireta de indivíduos por dedução ou exclusão estatística, o sistema vitAI oculta automaticamente as métricas agregadas deste time.
            </p>

            <div class="mt-2 rounded-lg border border-zinc-800 bg-zinc-900/60 p-3 text-xs text-zinc-400 space-y-1">
              <div class="font-medium text-zinc-200 flex items-center gap-1.5">
                <svg class="h-4 w-4 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                Princípio da Anonimização Efetiva (Portaria MTE nº 1.419/2024 & LGPD):
              </div>
              <p class="leading-relaxed">
                As respostas de pesquisas e sinais deste setor continuam sendo processados, porém consolidados exclusivamente no agrupamento macro da diretoria para assegurar sigilo absoluto.
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- Caso B: Área com N >= 5 (Painel de Sinais Completo) -->
      <section
        *ngIf="!comparison.isAnonymized && comparison.headcount >= 5"
        class="space-y-4"
      >
        <div class="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-800/80 pb-3">
          <div>
            <h3 class="text-base font-semibold text-white flex items-center gap-2">
              Sinais do Setor: {{ comparison.areaName }}
              <span class="text-xs font-mono font-normal text-zinc-400 bg-zinc-900 border border-zinc-800 px-2 py-0.5 rounded">
                {{ comparison.headcount }} colaboradores
              </span>
            </h3>
            <p class="text-xs text-zinc-400">
              Série histórica agregada dos últimos 6 meses (Ponto, Folha e Clima)
            </p>
          </div>
          <span class="inline-flex items-center gap-1.5 rounded-md bg-zinc-900 border border-zinc-800 px-2.5 py-1 text-xs font-mono text-zinc-300">
            Quórum Elegível para Auditoria NR-1
          </span>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div class="rounded-lg bg-zinc-950 p-3 border border-zinc-800">
            <span class="block text-[11px] text-zinc-400">Variação de Atestados</span>
            <div class="mt-1 flex items-baseline gap-1">
              <span
                class="text-xl font-bold font-mono"
                [ngClass]="comparison.variacaoDiasAtestadoPct > 20 ? 'text-rose-400' : 'text-zinc-100'"
              >
                {{ comparison.variacaoDiasAtestadoPct > 0 ? '+' : '' }}{{ comparison.variacaoDiasAtestadoPct }}%
              </span>
            </div>
          </div>

          <div class="rounded-lg bg-zinc-950 p-3 border border-zinc-800">
            <span class="block text-[11px] text-zinc-400">Variação de Horas Extras</span>
            <div class="mt-1 flex items-baseline gap-1">
              <span
                class="text-xl font-bold font-mono"
                [ngClass]="comparison.variacaoHorasExtrasPct > 20 ? 'text-rose-400' : 'text-zinc-100'"
              >
                {{ comparison.variacaoHorasExtrasPct > 0 ? '+' : '' }}{{ comparison.variacaoHorasExtrasPct }}%
              </span>
            </div>
          </div>

          <div class="rounded-lg bg-zinc-950 p-3 border border-zinc-800">
            <span class="block text-[11px] text-zinc-400">Saídas Voluntárias</span>
            <div class="mt-1 flex items-baseline gap-1">
              <span class="text-xl font-bold font-mono text-amber-400">
                {{ comparison.pedidosDemissaoPeriodo }}
              </span>
              <span class="text-[10px] font-mono text-zinc-500">média: {{ comparison.mediaEmpresaPedidosDemissao }}</span>
            </div>
          </div>

          <div class="rounded-lg bg-zinc-950 p-3 border border-zinc-800">
            <span class="block text-[11px] text-zinc-400">Nota de Carga</span>
            <div class="mt-1 flex items-baseline gap-1">
              <span
                class="text-xl font-bold font-mono"
                [ngClass]="comparison.notaCargaTrabalhoAtual && comparison.notaCargaTrabalhoAtual < 3 ? 'text-rose-400' : 'text-zinc-100'"
              >
                {{ comparison.notaCargaTrabalhoAtual || 'N/D' }}
              </span>
              <span *ngIf="comparison.notaCargaTrabalhoAnterior" class="text-[10px] font-mono text-zinc-500 line-through">
                {{ comparison.notaCargaTrabalhoAnterior }}
              </span>
            </div>
          </div>
        </div>

        <!-- Eventos de Contexto da Área -->
        <div *ngIf="comparison.eventosContextoRecentes && comparison.eventosContextoRecentes.length > 0" class="space-y-2 pt-2 border-t border-zinc-800/80">
          <h4 class="text-xs font-semibold uppercase tracking-wider text-zinc-400">
            Linha do Tempo de Eventos Corporativos
          </h4>
          <ul class="space-y-1.5 text-xs text-zinc-300">
            <li *ngFor="let ev of comparison.eventosContextoRecentes" class="flex items-start gap-2 bg-zinc-950 p-2.5 rounded-lg border border-zinc-800">
              <span class="mt-1.5 h-1.5 w-1.5 rounded-full bg-zinc-400 shrink-0"></span>
              <span>{{ ev }}</span>
            </li>
          </ul>
        </div>
      </section>
    </div>
  `,
})
export class AreaSignalsViewComponent {
  @Input() comparison!: AreaHistoryComparison;
}
