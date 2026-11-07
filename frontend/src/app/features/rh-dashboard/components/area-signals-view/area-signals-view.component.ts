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
        class="relative overflow-hidden rounded-2xl border border-zinc-800 bg-gradient-to-br from-[#121118] via-zinc-950 to-[#121118] p-6 backdrop-blur-md shadow-[0_0_30px_rgba(204,255,0,0.06)]"
      >
        <div class="flex items-start gap-4">
          <!-- Ícone de Escudo de Privacidade LGPD em Verde-Lima Neon -->
          <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-zinc-900 border border-[#CCFF00]/40 text-[#CCFF00] shadow-[0_0_20px_rgba(204,255,0,0.25)]">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
          </div>

          <div class="flex-1 space-y-2">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <span class="inline-flex items-center gap-1.5 rounded-full bg-zinc-900 border border-[#CCFF00]/40 px-3 py-1 text-xs font-mono font-bold text-[#CCFF00] shadow-[0_0_12px_rgba(204,255,0,0.15)]">
                <span class="h-2 w-2 rounded-full bg-[#CCFF00] shadow-[0_0_6px_#CCFF00] animate-pulse"></span>
                Shield LGPD (N &lt; 5) &bull; Blindagem Ativa
              </span>
              <span class="text-xs font-mono text-zinc-400">Headcount Real = {{ comparison.headcount }} pessoas</span>
            </div>

            <h3 class="text-lg font-bold text-white flex items-center gap-2">
              Área: {{ comparison.areaName }}
              <span class="text-xs font-mono font-normal text-zinc-500 bg-zinc-900 px-2 py-0.5 rounded border border-zinc-800">
                Dados Agregados Ocultados
              </span>
            </h3>

            <p class="text-sm text-zinc-300 leading-relaxed">
              Esta equipe possui <strong>{{ comparison.headcount }} colaboradores</strong> (quórum inferior ao limite mínimo de <strong>5 pessoas</strong> exigido para análises coletivas).
              Para impedir a identificação indireta de indivíduos por dedução ou exclusão estatística, o sistema VYTAL.ai oculta automaticamente as métricas agregadas deste time.
            </p>

            <div class="mt-3 rounded-xl border border-zinc-800 bg-zinc-900/80 p-3.5 text-xs text-zinc-300 space-y-1.5">
              <div class="font-bold text-[#CCFF00] flex items-center gap-1.5 font-mono">
                <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                Princípio da Anonimização Efetiva (Portaria MTE nº 1.419/2024 & LGPD):
              </div>
              <p class="text-zinc-400 leading-relaxed">
                As pesquisas de pulso e sinais deste time continuam sendo processados, mas apenas combinados ao agrupamento macro da diretoria para garantir 100% de sigilo dos colaboradores.
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- Caso B: Área com N >= 5 (Painel de Sinais Completo e Transparente) -->
      <section
        *ngIf="!comparison.isAnonymized && comparison.headcount >= 5"
        class="rounded-2xl border border-zinc-800 bg-[#121118]/90 p-6 backdrop-blur-md space-y-4"
      >
        <div class="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-800/80 pb-3">
          <div>
            <h3 class="text-lg font-bold text-white flex items-center gap-2">
              Sinais da Área: {{ comparison.areaName }}
              <span class="text-xs font-mono font-normal text-zinc-400 bg-zinc-900 border border-zinc-800 px-2 py-0.5 rounded">
                {{ comparison.headcount }} colaboradores
              </span>
            </h3>
            <p class="text-xs text-zinc-400">
              Série histórica agregada dos últimos 6 meses (Ponto, Folha e Clima)
            </p>
          </div>
          <span class="inline-flex items-center gap-1.5 rounded-full bg-zinc-900 border border-[#CCFF00]/30 px-3 py-1 text-xs font-mono text-[#CCFF00]">
            <span class="h-1.5 w-1.5 rounded-full bg-[#CCFF00] shadow-[0_0_6px_#CCFF00]"></span>
            Quórum Elegível para Auditoria NR-1
          </span>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div class="rounded-xl bg-zinc-900/80 p-3.5 border border-zinc-800/80">
            <span class="block text-[11px] font-medium text-zinc-400">Variação de Atestados</span>
            <div class="mt-1 flex items-baseline gap-1">
              <span
                class="text-2xl font-bold font-mono"
                [ngClass]="comparison.variacaoDiasAtestadoPct > 20 ? 'text-rose-400' : 'text-zinc-100'"
              >
                {{ comparison.variacaoDiasAtestadoPct > 0 ? '+' : '' }}{{ comparison.variacaoDiasAtestadoPct }}%
              </span>
            </div>
          </div>

          <div class="rounded-xl bg-zinc-900/80 p-3.5 border border-zinc-800/80">
            <span class="block text-[11px] font-medium text-zinc-400">Variação de Horas Extras</span>
            <div class="mt-1 flex items-baseline gap-1">
              <span
                class="text-2xl font-bold font-mono"
                [ngClass]="comparison.variacaoHorasExtrasPct > 20 ? 'text-rose-400' : 'text-zinc-100'"
              >
                {{ comparison.variacaoHorasExtrasPct > 0 ? '+' : '' }}{{ comparison.variacaoHorasExtrasPct }}%
              </span>
            </div>
          </div>

          <div class="rounded-xl bg-zinc-900/80 p-3.5 border border-zinc-800/80">
            <span class="block text-[11px] font-medium text-zinc-400">Saídas Voluntárias</span>
            <div class="mt-1 flex items-baseline gap-1">
              <span class="text-2xl font-bold font-mono text-amber-400">
                {{ comparison.pedidosDemissaoPeriodo }}
              </span>
              <span class="text-[10px] font-mono text-zinc-500">média: {{ comparison.mediaEmpresaPedidosDemissao }}</span>
            </div>
          </div>

          <div class="rounded-xl bg-zinc-900/80 p-3.5 border border-zinc-800/80">
            <span class="block text-[11px] font-medium text-zinc-400">Nota de Carga</span>
            <div class="mt-1 flex items-baseline gap-1">
              <span
                class="text-2xl font-bold font-mono"
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
          <h4 class="text-xs font-bold uppercase tracking-wider text-violet-300 flex items-center gap-1.5 font-mono">
            <svg class="h-4 w-4 text-[#8B5CF6]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            Linha do Tempo de Eventos Corporativos
          </h4>
          <ul class="space-y-1.5 text-xs text-zinc-300">
            <li *ngFor="let ev of comparison.eventosContextoRecentes" class="flex items-start gap-2 bg-zinc-900/60 p-2.5 rounded-xl border border-zinc-800/60">
              <span class="mt-1.5 h-1.5 w-1.5 rounded-full bg-[#8B5CF6] shadow-[0_0_6px_#8B5CF6] shrink-0"></span>
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
