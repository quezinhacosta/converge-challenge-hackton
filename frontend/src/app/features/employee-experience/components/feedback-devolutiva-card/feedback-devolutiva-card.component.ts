import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-feedback-devolutiva-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="rounded-xl border border-emerald-200 bg-emerald-50/60 p-6 shadow-sm">
      <div class="flex items-center gap-2 text-emerald-800">
        <span class="rounded-full bg-emerald-200 px-2.5 py-0.5 text-xs font-bold uppercase tracking-wider">
          Você falou, a empresa fez
        </span>
        <span class="text-xs text-emerald-700">Equipe: {{ areaName }}</span>
      </div>

      <h3 class="mt-2 text-lg font-bold text-slate-900">
        Comunicado de Melhoria e Cuidado com a Equipe
      </h3>

      <div class="mt-3 space-y-2 text-sm text-slate-700">
        <div>
          <strong class="text-slate-900">O que ouvimos de vocês:</strong>
          {{ summaryOfListening }}
        </div>
        <div class="rounded-lg bg-white p-3 border border-emerald-100 text-slate-800">
          <strong class="text-emerald-900">O que vai mudar a partir de agora:</strong>
          {{ actionPlanExplanation }}
        </div>
      </div>
    </div>
  `,
})
export class FeedbackDevolutivaCardComponent {
  @Input() areaName = 'Atendimento ao Cliente';
  @Input() summaryOfListening =
    'Sobrecarga percebida após implantação da nova meta de atendimentos por hora em agosto.';
  @Input() actionPlanExplanation =
    'Revisão da meta junto à liderança e realização de círculos de escuta periódicos com apoio do RH.';
}
