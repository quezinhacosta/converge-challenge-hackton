import { Component, Input, Output, EventEmitter } from '@angular/core';
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
        class="relative overflow-hidden rounded-2xl border border-amber-200/90 bg-gradient-to-br from-amber-50/90 via-white to-amber-50/50 p-6 shadow-sm"
      >
        <div class="flex items-start gap-4">
          <!-- Ícone de Escudo de Privacidade LGPD -->
          <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-amber-500 text-white shadow-sm ring-4 ring-amber-100">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
          </div>

          <div class="flex-1 space-y-2">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <span class="inline-flex items-center gap-1.5 rounded-full bg-amber-100 px-3 py-0.5 text-xs font-bold text-amber-900 border border-amber-200">
                <svg class="h-3.5 w-3.5 text-amber-700" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                </svg>
                Bloqueado por Guardrail LGPD &bull; Quórum Mínimo Não Atingido
              </span>
              <span class="text-xs font-mono text-slate-500">N = {{ comparison.headcount }} pessoas</span>
            </div>

            <h3 class="text-lg font-bold text-slate-900">
              Área: {{ comparison.areaName }} (Dados Ocultados)
            </h3>

            <p class="text-sm text-slate-700 leading-relaxed">
              Esta equipe possui <strong>{{ comparison.headcount }} colaboradores</strong> (quórum inferior ao limite de segurança de <strong>5 pessoas</strong>).
              Para impedir a identificação indireta de indivíduos por dedução ou exclusão estatística, o VytAI oculta automaticamente as métricas agregadas desta área.
            </p>

            <div class="mt-3 rounded-xl border border-amber-200 bg-white/80 p-3.5 text-xs text-amber-900 space-y-1.5">
              <div class="font-bold flex items-center gap-1.5">
                <svg class="h-4 w-4 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                Princípio da Anonimização Efetiva (Portaria MTE nº 1.419/2024 & LGPD):
              </div>
              <p class="text-slate-600 leading-relaxed">
                As pesquisas de pulso e sinais de ponto deste time continuam sendo processados, mas apenas combinados ao agrupamento macro da diretoria ou gerência para garantir 100% de sigilo dos colaboradores.
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- Caso B: Área com N >= 5 (Painel de Sinais Completo e Transparente) -->
      <section
        *ngIf="!comparison.isAnonymized && comparison.headcount >= 5"
        class="overflow-hidden rounded-2xl border border-slate-200 bg-white p-6 shadow-sm hover:shadow-md transition-shadow"
      >
        <header class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-4">
          <div>
            <div class="flex items-center gap-2">
              <span class="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-800 border border-emerald-200">
                <span class="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
                Quórum Válido (LGPD OK)
              </span>
              <span class="text-xs text-slate-500">&bull; {{ comparison.headcount }} pessoas monitoradas</span>
            </div>
            <h3 class="mt-1 text-lg font-bold text-slate-900">
              Sinais Operacionais: {{ comparison.areaName }}
            </h3>
          </div>

          <div class="flex items-center gap-2">
            <span class="text-xs text-slate-500 font-mono">Área ID: {{ comparison.areaId }}</span>
          </div>
        </header>

        <!-- Indicadores Numéricos em Grid com Barras de Saúde -->
        <div class="mt-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
          <!-- Card de Atestados -->
          <div class="rounded-xl border border-slate-200/80 bg-slate-50/60 p-4">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold text-slate-600">Variação de Dias de Atestado</span>
              <span
                class="rounded px-2 py-0.5 text-xs font-bold font-mono"
                [ngClass]="comparison.variacaoDiasAtestadoPct > 20 ? 'bg-rose-100 text-rose-700' : 'bg-slate-200 text-slate-700'"
              >
                {{ comparison.variacaoDiasAtestadoPct > 0 ? '+' : '' }}{{ comparison.variacaoDiasAtestadoPct }}%
              </span>
            </div>

            <!-- Barra Visual de Proporção -->
            <div class="mt-3 h-2 w-full overflow-hidden rounded-full bg-slate-200">
              <div
                class="h-full rounded-full transition-all duration-500"
                [ngClass]="comparison.variacaoDiasAtestadoPct > 20 ? 'bg-rose-500' : 'bg-emerald-500'"
                [style.width.%]="Math.min(100, Math.max(10, comparison.variacaoDiasAtestadoPct + 30))"
              ></div>
            </div>
            <p class="mt-2 text-[11px] text-slate-500">
              Comparativo trimestral vs histórico anterior da própria equipe.
            </p>
          </div>

          <!-- Card de Horas Extras -->
          <div class="rounded-xl border border-slate-200/80 bg-slate-50/60 p-4">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold text-slate-600">Variação de Horas Extras</span>
              <span
                class="rounded px-2 py-0.5 text-xs font-bold font-mono"
                [ngClass]="comparison.variacaoHorasExtrasPct > 20 ? 'bg-rose-100 text-rose-700' : 'bg-slate-200 text-slate-700'"
              >
                {{ comparison.variacaoHorasExtrasPct > 0 ? '+' : '' }}{{ comparison.variacaoHorasExtrasPct }}%
              </span>
            </div>

            <div class="mt-3 h-2 w-full overflow-hidden rounded-full bg-slate-200">
              <div
                class="h-full rounded-full transition-all duration-500"
                [ngClass]="comparison.variacaoHorasExtrasPct > 20 ? 'bg-rose-500' : 'bg-emerald-500'"
                [style.width.%]="Math.min(100, Math.max(10, comparison.variacaoHorasExtrasPct + 25))"
              ></div>
            </div>
            <p class="mt-2 text-[11px] text-slate-500">
              Indicador de sobrecarga física e psicológica contínua.
            </p>
          </div>

          <!-- Card de Demissões Voluntárias -->
          <div class="rounded-xl border border-slate-200/80 bg-slate-50/60 p-4">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold text-slate-600">Pedidos de Demissão no Período</span>
              <span class="text-sm font-bold font-mono text-slate-900">
                {{ comparison.pedidosDemissaoPeriodo }} saídas
                <span class="text-xs font-normal text-slate-500">(média da empresa: {{ comparison.mediaEmpresaPedidosDemissao }})</span>
              </span>
            </div>
            <p class="mt-2 text-[11px] text-slate-500">
              Turnover voluntário atípico correlacionado a fatores psicossociais.
            </p>
          </div>

          <!-- Card de Pesquisa VytAI (Nota de Carga) -->
          <div class="rounded-xl border border-slate-200/80 bg-slate-50/60 p-4" *ngIf="comparison.notaCargaTrabalhoAtual">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold text-slate-600">Nota de Carga na Pesquisa VytAI</span>
              <span class="text-sm font-bold font-mono" [ngClass]="comparison.notaCargaTrabalhoAtual < 3 ? 'text-rose-600' : 'text-emerald-600'">
                {{ comparison.notaCargaTrabalhoAtual }} / 5.0
                <span class="text-xs font-normal text-slate-400 line-through" *ngIf="comparison.notaCargaTrabalhoAnterior">
                  ({{ comparison.notaCargaTrabalhoAnterior }})
                </span>
              </span>
            </div>
            <p class="mt-2 text-[11px] text-slate-500">
              Média anônima das respostas dos colaboradores da área.
            </p>
          </div>
        </div>

        <!-- Timeline de Eventos de Contexto Recentes -->
        <div class="mt-5 rounded-xl border border-slate-100 bg-slate-50/50 p-4" *ngIf="comparison.eventosContextoRecentes.length > 0">
          <h4 class="text-xs font-bold uppercase tracking-wider text-slate-600 flex items-center gap-1.5 mb-2">
            <svg class="h-4 w-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
            Linha do Tempo de Mudanças Organizacionais (Contexto)
          </h4>
          <ul class="space-y-1.5 text-xs text-slate-700">
            <li *ngFor="let ev of comparison.eventosContextoRecentes" class="flex items-start gap-2">
              <span class="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-indigo-500"></span>
              <span>{{ ev }}</span>
            </li>
          </ul>
        </div>
      </section>
    </div>
  `,
})
export class AreaSignalsViewComponent {
  @Input({ required: true }) comparison!: AreaHistoryComparison;

  protected readonly Math = Math;
}
