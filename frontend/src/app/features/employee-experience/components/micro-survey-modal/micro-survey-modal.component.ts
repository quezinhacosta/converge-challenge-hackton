import { Component, Input, Output, EventEmitter, signal } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-micro-survey-modal',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div
      *ngIf="isOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4 animate-fadeIn"
    >
      <div class="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl border border-slate-200 space-y-5">
        <!-- Header do Modal -->
        <header class="flex items-start justify-between border-b border-slate-100 pb-4">
          <div class="flex items-center gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600 ring-4 ring-indigo-50/50">
              <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div>
              <div class="flex items-center gap-2">
                <h3 class="text-base font-bold text-slate-900">{{ title }}</h3>
                <span class="rounded bg-indigo-100 px-2 py-0.2 text-[10px] font-semibold text-indigo-800">
                  Leva 30 segundos
                </span>
              </div>
              <p class="text-xs text-slate-500 mt-0.5">
                Check-in anônimo mensal de saúde e bem-estar do time (Portaria MTE nº 1.419/2024).
              </p>
            </div>
          </div>

          <button
            type="button"
            (click)="onClose()"
            class="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors"
          >
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </header>

        <!-- Garantia Explícita de Privacidade -->
        <div class="flex items-center gap-2 rounded-xl bg-emerald-50 px-3.5 py-2 text-xs text-emerald-800 border border-emerald-200">
          <svg class="h-4 w-4 shrink-0 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
          </svg>
          <span><strong>100% Anônimo:</strong> Sua resposta é agregada à média da equipe sem identificação de IP ou usuário.</span>
        </div>

        <!-- 3 Perguntas Rápidas com Escala Likert de 1 a 5 -->
        <div class="space-y-4 text-xs text-slate-700">
          <!-- Pergunta 1 -->
          <div class="rounded-xl border border-slate-100 bg-slate-50/60 p-3.5 space-y-2">
            <label class="block font-semibold text-slate-800">
              1. Como você avalia o volume e o ritmo da sua carga de trabalho este mês?
            </label>
            <div class="grid grid-cols-5 gap-1.5 pt-1">
              <button
                *ngFor="let val of [1, 2, 3, 4, 5]"
                type="button"
                (click)="q1.set(val)"
                class="rounded-lg border py-2 text-center font-bold text-xs transition-all shadow-xs"
                [ngClass]="q1() === val ? 'border-indigo-600 bg-indigo-600 text-white' : 'border-slate-200 bg-white text-slate-700 hover:border-indigo-300 hover:bg-indigo-50'"
              >
                {{ val }}
              </button>
            </div>
            <div class="flex justify-between text-[10px] text-slate-400 px-1">
              <span>1 = Muito Excessivo</span>
              <span>5 = Equilibrado e Sustentável</span>
            </div>
          </div>

          <!-- Pergunta 2 -->
          <div class="rounded-xl border border-slate-100 bg-slate-50/60 p-3.5 space-y-2">
            <label class="block font-semibold text-slate-800">
              2. Você tem clareza das prioridades e autonomia para organizar suas tarefas?
            </label>
            <div class="grid grid-cols-5 gap-1.5 pt-1">
              <button
                *ngFor="let val of [1, 2, 3, 4, 5]"
                type="button"
                (click)="q2.set(val)"
                class="rounded-lg border py-2 text-center font-bold text-xs transition-all shadow-xs"
                [ngClass]="q2() === val ? 'border-indigo-600 bg-indigo-600 text-white' : 'border-slate-200 bg-white text-slate-700 hover:border-indigo-300 hover:bg-indigo-50'"
              >
                {{ val }}
              </button>
            </div>
            <div class="flex justify-between text-[10px] text-slate-400 px-1">
              <span>1 = Totalmente Confuso</span>
              <span>5 = Clareza Total</span>
            </div>
          </div>

          <!-- Pergunta 3 -->
          <div class="rounded-xl border border-slate-100 bg-slate-50/60 p-3.5 space-y-2">
            <label class="block font-semibold text-slate-800">
              3. Você se sente seguro psicologicamente e apoiado pela liderança imediata?
            </label>
            <div class="grid grid-cols-5 gap-1.5 pt-1">
              <button
                *ngFor="let val of [1, 2, 3, 4, 5]"
                type="button"
                (click)="q3.set(val)"
                class="rounded-lg border py-2 text-center font-bold text-xs transition-all shadow-xs"
                [ngClass]="q3() === val ? 'border-indigo-600 bg-indigo-600 text-white' : 'border-slate-200 bg-white text-slate-700 hover:border-indigo-300 hover:bg-indigo-50'"
              >
                {{ val }}
              </button>
            </div>
            <div class="flex justify-between text-[10px] text-slate-400 px-1">
              <span>1 = Sem Nenhum Apoio</span>
              <span>5 = Apoio Pleno</span>
            </div>
          </div>
        </div>

        <!-- Mensagem de Sucesso pós-envio -->
        <div *ngIf="submitted()" class="rounded-xl bg-emerald-100 p-3 text-xs font-semibold text-emerald-800 text-center">
          Obrigado! Sua contribuição anônima foi integrada aos indicadores do time.
        </div>

        <!-- Rodapé do Modal -->
        <footer class="flex items-center justify-end gap-2 border-t border-slate-100 pt-4">
          <button
            type="button"
            (click)="onClose()"
            class="rounded-xl px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 transition-colors"
          >
            Cancelar
          </button>
          <button
            type="button"
            [disabled]="submitted()"
            (click)="onSubmit()"
            class="rounded-xl bg-indigo-600 px-4 py-2 text-xs font-bold text-white shadow-xs hover:bg-indigo-700 active:scale-95 disabled:opacity-50 transition-all"
          >
            Enviar Respostas Anônimas
          </button>
        </footer>
      </div>
    </div>
  `,
})
export class MicroSurveyModalComponent {
  @Input() isOpen = false;
  @Input() title = 'Check-in de Clima & Carga de Trabalho';
  @Output() close = new EventEmitter<void>();
  @Output() submitSurvey = new EventEmitter<void>();

  q1 = signal(3);
  q2 = signal(4);
  q3 = signal(4);
  submitted = signal(false);

  onClose(): void {
    this.submitted.set(false);
    this.close.emit();
  }

  onSubmit(): void {
    this.submitted.set(true);
    setTimeout(() => {
      this.submitSurvey.emit();
      this.onClose();
    }, 1000);
  }
}
