import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AreaHistoryComparison } from '../../../../core/models/signals.model';

@Component({
  selector: 'app-area-signals-view',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div *ngIf="comparison" class="space-y-6">
      <!-- Caso A: Área com menos de 5 pessoas (Quórum insuficiente - Proteção LGPD por exclusão) -->
      <section
        *ngIf="comparison.isAnonymized || comparison.headcount < 5"
        class="relative overflow-hidden rounded-2xl border border-zinc-700/80 bg-gradient-to-br from-zinc-900/95 via-[#0e0e14] to-zinc-950/95 p-8 shadow-2xl backdrop-blur-xl"
      >
        <div class="absolute -right-16 -top-16 w-56 h-56 bg-violet-600/10 rounded-full blur-3xl pointer-events-none animate-pulse-glow"></div>

        <div class="flex items-start gap-5">
          <!-- Ícone de Proteção com Borda em Gradiente -->
          <div class="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-tr from-violet-600 to-indigo-600 text-white shadow-lg shadow-violet-900/50 border border-violet-400/30">
            <svg class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
          </div>

          <div class="flex-1 space-y-3">
            <div class="flex flex-wrap items-center justify-between gap-3">
              <span class="inline-flex items-center gap-2 rounded-xl bg-violet-950/60 border border-violet-700/60 px-3.5 py-1 text-xs font-mono font-bold text-violet-200 shadow-sm">
                <span class="relative flex h-2 w-2">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-violet-400 opacity-75"></span>
                  <span class="relative inline-flex rounded-full h-2 w-2 bg-violet-500"></span>
                </span>
                Blindagem LGPD Ativa (N &lt; 5) &bull; Bloqueio Automático
              </span>
              <span class="text-xs font-mono font-bold text-zinc-300 bg-zinc-800/80 px-3 py-1 rounded-lg border border-zinc-700">
                Headcount Real = {{ comparison.headcount }} colaboradores
              </span>
            </div>

            <h3 class="text-xl font-black text-white flex items-center gap-3">
              <span>Setor: {{ comparison.areaName }}</span>
              <span class="text-xs font-mono font-bold text-rose-300 bg-rose-950/60 px-3 py-1 rounded-lg border border-rose-800/60">
                Dados Agregados Ocultados
              </span>
            </h3>

            <p class="text-sm text-zinc-200 leading-relaxed font-medium">
              Esta equipe possui <strong>{{ comparison.headcount }} colaboradores</strong> (quórum inferior ao limite mínimo de <strong>5 pessoas</strong> exigido por lei para análises coletivas).
              Para impedir a identificação indireta de indivíduos por dedução ou exclusão estatística, o sistema vitAI oculta automaticamente as métricas agregadas deste time.
            </p>

            <div class="mt-4 rounded-xl border border-zinc-800 bg-[#07070b]/90 p-4 text-xs text-zinc-300 space-y-1.5 shadow-inner">
              <div class="font-bold text-violet-300 flex items-center gap-2 font-mono">
                <svg class="h-4 w-4 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                Princípio da Anonimização Efetiva (Portaria MTE nº 1.419/2024 & LGPD):
              </div>
              <p class="leading-relaxed text-zinc-300 font-medium">
                As pesquisas de pulso e apontamentos deste time continuam sendo processados pela inteligência artificial, mas apenas agregados aos relatórios macro da diretoria para assegurar 100% de sigilo dos profissionais.
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- Caso B: Área com N >= 5 (Painel Completo) -->
      <section
        *ngIf="!comparison.isAnonymized && comparison.headcount >= 5"
        class="space-y-5"
      >
        <div class="flex flex-wrap items-center justify-between gap-4 border-b border-zinc-800/80 pb-4">
          <div>
            <h3 class="text-xl font-black text-white flex items-center gap-3">
              <span>Sinais do Setor: {{ comparison.areaName }}</span>
              <span class="text-xs font-mono font-bold text-zinc-200 bg-zinc-800 border border-zinc-700 px-3 py-1 rounded-lg">
                {{ comparison.headcount }} colaboradores
              </span>
            </h3>
            <p class="text-sm text-zinc-300 font-medium mt-0.5">
              Série histórica agregada dos últimos 6 meses (Ponto, Folha e Clima)
            </p>
          </div>
          <span class="inline-flex items-center gap-2 rounded-xl bg-zinc-900 border border-zinc-700 px-3.5 py-1.5 text-xs font-mono font-bold text-teal-300 shadow-sm">
            <span class="h-2 w-2 rounded-full bg-teal-400 animate-pulse"></span>
            Quórum Elegível para Auditoria NR-1
          </span>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div class="rounded-xl bg-zinc-900/90 p-4 border border-zinc-800 shadow-md">
            <span class="block text-xs font-semibold text-zinc-300">Variação de Atestados</span>
            <div class="mt-1.5 flex items-baseline gap-1">
              <span
                class="text-3xl font-black font-mono tracking-tight"
                [ngClass]="comparison.variacaoDiasAtestadoPct > 20 ? 'text-rose-400' : 'text-white'"
              >
                {{ comparison.variacaoDiasAtestadoPct > 0 ? '+' : '' }}{{ comparison.variacaoDiasAtestadoPct }}%
              </span>
            </div>
          </div>

          <div class="rounded-xl bg-zinc-900/90 p-4 border border-zinc-800 shadow-md">
            <span class="block text-xs font-semibold text-zinc-300">Variação de Horas Extras</span>
            <div class="mt-1.5 flex items-baseline gap-1">
              <span
                class="text-3xl font-black font-mono tracking-tight"
                [ngClass]="comparison.variacaoHorasExtrasPct > 20 ? 'text-rose-400' : 'text-white'"
              >
                {{ comparison.variacaoHorasExtrasPct > 0 ? '+' : '' }}{{ comparison.variacaoHorasExtrasPct }}%
              </span>
            </div>
          </div>

          <div class="rounded-xl bg-zinc-900/90 p-4 border border-zinc-800 shadow-md">
            <span class="block text-xs font-semibold text-zinc-300">Saídas Voluntárias</span>
            <div class="mt-1.5 flex items-baseline gap-1">
              <span class="text-3xl font-black font-mono text-amber-400 tracking-tight">
                {{ comparison.pedidosDemissaoPeriodo }}
              </span>
              <span class="text-xs font-mono text-zinc-400 font-semibold ml-1">média: {{ comparison.mediaEmpresaPedidosDemissao }}</span>
            </div>
          </div>

          <div class="rounded-xl bg-zinc-900/90 p-4 border border-zinc-800 shadow-md">
            <span class="block text-xs font-semibold text-zinc-300">Nota de Carga</span>
            <div class="mt-1.5 flex items-baseline gap-1">
              <span
                class="text-3xl font-black font-mono tracking-tight"
                [ngClass]="comparison.notaCargaTrabalhoAtual && comparison.notaCargaTrabalhoAtual < 3 ? 'text-rose-400' : 'text-white'"
              >
                {{ comparison.notaCargaTrabalhoAtual || 'N/D' }}
              </span>
              <span *ngIf="comparison.notaCargaTrabalhoAnterior" class="text-xs font-mono text-zinc-400 line-through ml-1 font-semibold">
                {{ comparison.notaCargaTrabalhoAnterior }}
              </span>
            </div>
          </div>
        </div>

        <!-- Linha do Tempo de Eventos -->
        <div *ngIf="comparison.eventosContextoRecentes && comparison.eventosContextoRecentes.length > 0" class="space-y-3 pt-3 border-t border-zinc-800/80">
          <h4 class="text-xs font-bold uppercase tracking-wider text-violet-300 flex items-center gap-2 font-mono">
            <svg class="h-4 w-4 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            Linha do Tempo de Eventos Organizacionais
          </h4>
          <ul class="space-y-2 text-sm text-zinc-200">
            <li *ngFor="let ev of comparison.eventosContextoRecentes" class="flex items-start gap-3 bg-zinc-900/80 p-3.5 rounded-xl border border-zinc-800 shadow-sm font-medium">
              <span class="mt-1.5 h-2 w-2 rounded-full bg-violet-400 shrink-0"></span>
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
