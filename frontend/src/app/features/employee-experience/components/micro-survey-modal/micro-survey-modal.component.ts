import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-micro-survey-modal',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div
      *ngIf="isOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
    >
      <div class="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <h3 class="text-lg font-bold text-slate-900">{{ title }}</h3>
        <p class="mt-1 text-xs text-slate-500">
          Suas respostas são 100% anônimas e compõem a média do seu time.
        </p>

        <div class="mt-4 space-y-4 text-sm text-slate-700">
          <div>
            <label class="block font-medium">1. Como você avalia sua carga de trabalho este mês?</label>
            <div class="mt-1 flex gap-2">
              <button
                *ngFor="let val of [1, 2, 3, 4, 5]"
                type="button"
                class="flex-1 rounded-md border border-slate-200 py-1.5 text-center text-xs font-semibold hover:bg-indigo-50"
              >
                {{ val }}
              </button>
            </div>
          </div>
          <div>
            <label class="block font-medium">2. Você sente clareza sobre suas prioridades e metas?</label>
            <div class="mt-1 flex gap-2">
              <button
                *ngFor="let val of [1, 2, 3, 4, 5]"
                type="button"
                class="flex-1 rounded-md border border-slate-200 py-1.5 text-center text-xs font-semibold hover:bg-indigo-50"
              >
                {{ val }}
              </button>
            </div>
          </div>
          <div>
            <label class="block font-medium">3. Você se sente apoiado pela sua liderança?</label>
            <div class="mt-1 flex gap-2">
              <button
                *ngFor="let val of [1, 2, 3, 4, 5]"
                type="button"
                class="flex-1 rounded-md border border-slate-200 py-1.5 text-center text-xs font-semibold hover:bg-indigo-50"
              >
                {{ val }}
              </button>
            </div>
          </div>
        </div>

        <div class="mt-6 flex justify-end gap-2 border-t border-slate-100 pt-4">
          <button
            type="button"
            (click)="onClose()"
            class="rounded-md px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-100"
          >
            Fechar
          </button>
          <button
            type="button"
            (click)="onSubmit()"
            class="rounded-md bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-indigo-700"
          >
            Enviar Respostas Anônimas
          </button>
        </div>
      </div>
    </div>
  `,
})
export class MicroSurveyModalComponent {
  @Input() isOpen = false;
  @Input() title = 'Check-in Rápido de Bem-Estar e Carga';
  @Output() close = new EventEmitter<void>();
  @Output() submitSurvey = new EventEmitter<void>();

  onClose(): void {
    this.close.emit();
  }

  onSubmit(): void {
    this.submitSurvey.emit();
  }
}
