import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-feedback-devolutiva-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <article class="overflow-hidden rounded-2xl border border-zinc-800 bg-[#121118]/90 backdrop-blur-md shadow-glass p-6 space-y-5">
      <!-- Header do Comunicado Transparente -->
      <header class="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-800/80 pb-4">
        <div class="flex items-center gap-2.5">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-zinc-900 border border-[#CCFF00]/40 text-[#CCFF00] shadow-[0_0_15px_rgba(204,255,0,0.25)]">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z"/>
            </svg>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="inline-flex items-center gap-1.5 rounded-full bg-zinc-900 border border-[#CCFF00]/30 px-2.5 py-0.5 text-[10px] font-mono font-bold uppercase tracking-wider text-[#CCFF00]">
                <span class="h-1.5 w-1.5 rounded-full bg-[#CCFF00] shadow-[0_0_6px_#CCFF00]"></span>
                Devolutiva Ativa &bull; NR-1
              </span>
              <span class="text-xs text-zinc-400 font-mono">Time: {{ areaName }}</span>
            </div>
            <h3 class="text-base font-bold text-white mt-1 flex items-center gap-2">
              Você falou, a empresa ouviu e agiu
            </h3>
          </div>
        </div>

        <span class="rounded-xl bg-zinc-900 border border-zinc-800 px-3 py-1 text-xs font-mono font-bold text-[#CCFF00]">
          Status: Homologado no PGR
        </span>
      </header>

      <!-- Mensagem de Contexto e Cuidado com a Equipe -->
      <p class="text-xs text-zinc-300 leading-relaxed">
        A sua participação na pesquisa mensal de pulso e nos canais de escuta orienta os ajustes de rotina na nossa empresa. Veja como os dados consolidados do seu time foram traduzidos em melhorias práticas:
      </p>

      <!-- Grade Bilateral: O Que Ouvimos vs O Que a Empresa Fez -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- O Que Ouvimos -->
        <div class="rounded-xl border border-zinc-800 bg-zinc-950/60 p-4 space-y-2">
          <div class="flex items-center gap-2 text-violet-300">
            <svg class="h-4 w-4 text-[#8B5CF6]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
            </svg>
            <h4 class="text-xs font-bold uppercase tracking-wider text-violet-300 font-mono">
              O Que Foi Identificado na Escuta
            </h4>
          </div>
          <p class="text-xs text-zinc-300 leading-relaxed font-mono">
            {{ listeningSummary }}
          </p>
        </div>

        <!-- O Que Foi Feito -->
        <div class="rounded-xl border border-zinc-800 bg-zinc-900/60 p-4 space-y-2">
          <div class="flex items-center gap-2 text-[#CCFF00]">
            <svg class="h-4 w-4 text-[#CCFF00]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <h4 class="text-xs font-bold uppercase tracking-wider text-[#CCFF00] font-mono">
              Ações Imediatas Adotadas no PGR
            </h4>
          </div>
          <p class="text-xs text-zinc-200 leading-relaxed">
            {{ actionPlan }}
          </p>
        </div>
      </div>

      <!-- Rodapé de Compromisso com o Colaborador -->
      <footer class="flex flex-wrap items-center justify-between gap-3 rounded-xl bg-zinc-950/80 border border-zinc-800/80 p-3.5 text-xs text-zinc-400 font-mono">
        <div class="flex items-center gap-2">
          <span class="h-2 w-2 rounded-xs bg-[#CCFF00] shadow-[0_0_6px_#CCFF00]"></span>
          <span>Ciclo de Escuta Ativa 100% Anônimo &bull; Respeito à LGPD e à NR-1</span>
        </div>
        <span class="text-zinc-500 text-[11px]">
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
