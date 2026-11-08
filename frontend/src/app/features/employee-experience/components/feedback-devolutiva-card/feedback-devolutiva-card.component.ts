import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-feedback-devolutiva-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <article class="rounded-2xl border border-zinc-700/80 bg-gradient-to-b from-zinc-900/90 to-zinc-950/90 p-8 space-y-6 shadow-2xl backdrop-blur-xl">
      <!-- Header do Comunicado -->
      <header class="flex flex-wrap items-center justify-between gap-4 border-b border-zinc-800/80 pb-5">
        <div class="flex items-center gap-3.5">
          <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-violet-600 to-indigo-600 text-white shadow-lg shadow-violet-900/50 border border-violet-400/30">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z"/>
            </svg>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="rounded-lg bg-violet-950/60 px-3 py-0.5 text-xs font-mono font-bold text-violet-300 border border-violet-800/60 shadow-sm">
                Devolutiva Ativa &bull; NR-1
              </span>
              <span class="text-xs text-zinc-300 font-mono font-bold">Setor: {{ areaName }}</span>
            </div>
            <h3 class="text-xl font-black text-white mt-1">
              Você falou, a empresa ouviu e agiu
            </h3>
          </div>
        </div>

        <span class="rounded-xl bg-zinc-900 border border-zinc-700 px-4 py-1.5 text-xs font-mono font-bold text-emerald-400 shadow-inner">
          Status: Homologado no PGR
        </span>
      </header>

      <!-- Mensagem de Contexto -->
      <p class="text-sm text-zinc-200 leading-relaxed font-medium">
        A sua participação nas pesquisas mensais de pulso e canais de escuta orienta diretamente as decisões operacionais da empresa. Confira as melhorias práticas adotadas a partir das considerações consolidadas do time:
      </p>

      <!-- Grade Bilateral: O Que Ouvimos vs O Que a Empresa Fez -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        <!-- O Que Ouvimos -->
        <div class="rounded-2xl border border-zinc-800 bg-[#09090d]/90 p-6 space-y-3 shadow-inner">
          <div class="flex items-center gap-2 text-violet-300">
            <svg class="h-5 w-5 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
            </svg>
            <h4 class="text-xs font-bold uppercase tracking-wider text-violet-300 font-mono">
              O Que Foi Identificado na Escuta
            </h4>
          </div>
          <p class="text-sm text-zinc-200 leading-relaxed font-mono">
            {{ listeningSummary }}
          </p>
        </div>

        <!-- O Que Foi Feito -->
        <div class="rounded-2xl border border-zinc-800 bg-[#09090d]/90 p-6 space-y-3 shadow-inner">
          <div class="flex items-center gap-2 text-emerald-400">
            <svg class="h-5 w-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <h4 class="text-xs font-bold uppercase tracking-wider text-emerald-400 font-mono">
              Ações Imediatas Adotadas no PGR
            </h4>
          </div>
          <p class="text-sm text-white leading-relaxed font-medium">
            {{ actionPlan }}
          </p>
        </div>
      </div>

      <!-- Rodapé -->
      <footer class="flex flex-wrap items-center justify-between gap-4 rounded-xl bg-zinc-950 p-4 text-xs text-zinc-300 font-mono border border-zinc-800">
        <div class="flex items-center gap-2 font-medium">
          <span class="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Ciclo de Escuta Ativa 100% Anônimo &bull; Respeito integral à LGPD e à NR-1</span>
        </div>
        <span class="text-zinc-400 text-xs">
          Próxima medição de acompanhamento: 60 dias
        </span>
      </footer>
    </article>
  `,
})
export class FeedbackDevolutivaCardComponent {
  @Input() areaName = 'Atendimento ao Cliente';
  @Input() listeningSummary =
    'Queda na percepção de equilíbrio da carga de trabalho (de 3.9 para 2.4) e aumento no cansaço relatado após o pico de chamados decorrente da nova meta.';
  @Input() actionPlan =
    'O RH e a diretoria acordaram com a liderança do setor uma repactuação imediata do volume de atendimentos por hora (-25%), além da abertura de sessões semanais de descompressão e mentoria de apoio.';
}
