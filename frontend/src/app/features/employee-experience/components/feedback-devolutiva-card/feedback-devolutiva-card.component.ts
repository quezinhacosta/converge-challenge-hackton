import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-feedback-devolutiva-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <article class="overflow-hidden rounded-2xl border border-emerald-200/90 bg-gradient-to-br from-white via-emerald-50/30 to-white shadow-sm hover:shadow-md transition-all p-6 space-y-5">
      <!-- Header do Comunicado Transparente -->
      <header class="flex flex-wrap items-center justify-between gap-3 border-b border-emerald-100 pb-4">
        <div class="flex items-center gap-2.5">
          <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-600 text-white shadow-xs">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z"/>
            </svg>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="inline-flex items-center rounded-full bg-emerald-100 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-emerald-800">
                Transparência &bull; Canal de Devolutiva NR-1
              </span>
              <span class="text-xs text-slate-500 font-medium">Equipe: {{ areaName }}</span>
            </div>
            <h3 class="text-base font-bold text-slate-900 mt-0.5">
              Você falou, a empresa ouviu e agiu
            </h3>
          </div>
        </div>

        <span class="rounded-lg bg-emerald-50 border border-emerald-200 px-2.5 py-1 text-[11px] font-semibold text-emerald-800">
          Status: Ação Homologada no PGR
        </span>
      </header>

      <!-- Mensagem de Contexto e Cuidado com a Equipe -->
      <p class="text-xs text-slate-600 leading-relaxed">
        A sua participação na pesquisa mensal de pulso e nos canais de escuta é o termômetro que orienta os investimentos em saúde física e mental na nossa empresa. Veja como os dados consolidados do seu time foram traduzidos em melhorias práticas:
      </p>

      <!-- Grade Bilateral: O Que Ouvimos vs O Que a Empresa Fez -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- O Que Ouvimos -->
        <div class="rounded-xl border border-slate-200/80 bg-white p-4 space-y-2 shadow-xs">
          <div class="flex items-center gap-2 text-slate-700">
            <svg class="h-4 w-4 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
            </svg>
            <h4 class="text-xs font-bold uppercase tracking-wider text-slate-800">
              O Que Foi Identificado na Escuta
            </h4>
          </div>
          <p class="text-xs text-slate-600 leading-relaxed">
            {{ summaryOfListening }}
          </p>
        </div>

        <!-- O Que Foi Feito -->
        <div class="rounded-xl border border-emerald-200 bg-emerald-50/70 p-4 space-y-2 shadow-xs">
          <div class="flex items-center gap-2 text-emerald-900">
            <svg class="h-4 w-4 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <h4 class="text-xs font-bold uppercase tracking-wider text-emerald-900">
              Plano de Ação Registrado no PGR
            </h4>
          </div>
          <p class="text-xs text-slate-800 font-medium leading-relaxed">
            {{ actionPlanExplanation }}
          </p>
        </div>
      </div>

      <!-- Próximos Passos e Ciclo de 60 Dias -->
      <footer class="rounded-xl border border-slate-100 bg-slate-50/60 p-3.5 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-600">
        <div class="flex items-center gap-2">
          <svg class="h-4 w-4 text-indigo-600 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <span><strong>Próxima etapa:</strong> Reavaliação de eficácia com a equipe em 60 dias para medir o impacto das mudanças.</span>
        </div>
        <span class="text-[11px] text-slate-400 font-mono">Conformidade NR-1 / Portaria MTE nº 1.419/2024</span>
      </footer>
    </article>
  `,
})
export class FeedbackDevolutivaCardComponent {
  @Input() areaName = 'Atendimento ao Cliente';
  @Input() summaryOfListening =
    'Queda na percepção de equilíbrio de carga de trabalho e sobrecarga de horas extras relatadas na pesquisa de pulso de outubro.';
  @Input() actionPlanExplanation =
    'Revisão imediata das metas de atendimento junto à diretoria, redistribuição da fila de chamados e implantação de círculos semanais de escuta mediada pelo RH.';
}
