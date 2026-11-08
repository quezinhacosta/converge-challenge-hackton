import { Component, Input, Output, EventEmitter, signal } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-micro-survey-modal',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div
      *ngIf="isOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-md p-4 animate-fadeIn"
    >
      <div class="w-full max-w-xl rounded-2xl bg-[#0d0d12] p-8 border border-zinc-700 shadow-2xl space-y-6">
        <!-- Header do Modal -->
        <header class="flex items-start justify-between border-b border-zinc-800 pb-4">
          <div class="flex items-center gap-3">
            <div class="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-tr from-violet-600 to-indigo-600 text-white shadow-md shadow-violet-900/50">
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div>
              <div class="flex items-center gap-2">
                <h3 class="text-lg font-black text-white">{{ title }}</h3>
                <span class="rounded-md bg-violet-950/60 px-2.5 py-0.5 text-xs font-mono font-bold text-violet-300 border border-violet-800/60">
                  Leva 30 segundos
                </span>
              </div>
              <p class="text-xs text-zinc-300 font-medium mt-0.5">
                Check-in anônimo mensal de bem-estar da equipe (Portaria MTE nº 1.419/2024).
              </p>
            </div>
          </div>

          <button
            type="button"
            (click)="onClose()"
            class="text-zinc-400 hover:text-white p-1 text-xl font-bold"
          >
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </header>

        <!-- Garantia de Anonimato -->
        <div class="rounded-xl bg-zinc-950 p-3.5 text-xs text-zinc-300 border border-zinc-800 font-mono flex items-center gap-2 shadow-inner">
          <span class="h-2 w-2 rounded-full bg-emerald-400 animate-pulse shrink-0"></span>
          <span><strong class="text-white">100% Anônimo:</strong> Sua resposta é agregada à média do setor sem qualquer identificação pessoal ou de IP.</span>
        </div>

        <!-- 3 Perguntas Rápidas com Escala Visual Nitida -->
        <div class="space-y-4 text-xs text-zinc-200">
          <!-- Pergunta 1 -->
          <div class="rounded-xl border border-zinc-800 bg-zinc-950/80 p-4 space-y-2.5 shadow-sm">
            <label class="block text-sm font-bold text-white">
              1. Como você avalia o volume e o ritmo da sua carga de trabalho este mês?
            </label>
            <div class="flex items-center justify-between gap-1.5 pt-1">
              <button
                *ngFor="let val of [1, 2, 3, 4, 5]"
                type="button"
                (click)="q1Answer.set(val)"
                class="flex-1 rounded-xl py-2 font-mono text-sm font-black transition-all border"
                [ngClass]="q1Answer() === val ? 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white border-violet-400 shadow-md shadow-violet-900/50 scale-105' : 'bg-zinc-900 border-zinc-800 text-zinc-400 hover:border-zinc-700 hover:text-white'"
              >
                {{ val }}
              </button>
            </div>
            <div class="flex justify-between text-xs text-zinc-400 font-mono font-medium">
              <span>Muito Pesada (1)</span>
              <span>Equilibrada (5)</span>
            </div>
          </div>

          <!-- Pergunta 2 -->
          <div class="rounded-xl border border-zinc-800 bg-zinc-950/80 p-4 space-y-2.5 shadow-sm">
            <label class="block text-sm font-bold text-white">
              2. Você sente que dispõe do apoio necessário da sua liderança para suas entregas?
            </label>
            <div class="flex items-center justify-between gap-1.5 pt-1">
              <button
                *ngFor="let val of [1, 2, 3, 4, 5]"
                type="button"
                (click)="q2Answer.set(val)"
                class="flex-1 rounded-xl py-2 font-mono text-sm font-black transition-all border"
                [ngClass]="q2Answer() === val ? 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white border-violet-400 shadow-md shadow-violet-900/50 scale-105' : 'bg-zinc-900 border-zinc-800 text-zinc-400 hover:border-zinc-700 hover:text-white'"
              >
                {{ val }}
              </button>
            </div>
            <div class="flex justify-between text-xs text-zinc-400 font-mono font-medium">
              <span>Pouco Apoio (1)</span>
              <span>Total Apoio (5)</span>
            </div>
          </div>

          <!-- Pergunta 3 -->
          <div class="rounded-xl border border-zinc-800 bg-zinc-950/80 p-4 space-y-2.5 shadow-sm">
            <label class="block text-sm font-bold text-white">
              3. O ambiente interpessoal do seu time tem sido respeitoso e acolhedor?
            </label>
            <div class="flex items-center justify-between gap-1.5 pt-1">
              <button
                *ngFor="let val of [1, 2, 3, 4, 5]"
                type="button"
                (click)="q3Answer.set(val)"
                class="flex-1 rounded-xl py-2 font-mono text-sm font-black transition-all border"
                [ngClass]="q3Answer() === val ? 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white border-violet-400 shadow-md shadow-violet-900/50 scale-105' : 'bg-zinc-900 border-zinc-800 text-zinc-400 hover:border-zinc-700 hover:text-white'"
              >
                {{ val }}
              </button>
            </div>
            <div class="flex justify-between text-xs text-zinc-400 font-mono font-medium">
              <span>Conflituoso (1)</span>
              <span>Harmonioso (5)</span>
            </div>
          </div>
        </div>

        <!-- Footer com Ação -->
        <footer class="flex items-center justify-end gap-3 pt-4 border-t border-zinc-800">
          <button
            type="button"
            (click)="onClose()"
            class="rounded-xl border border-zinc-700 bg-zinc-800 hover:bg-zinc-700 px-4 py-2.5 text-xs font-bold text-zinc-300 transition-all"
          >
            Cancelar
          </button>
          <button
            type="button"
            (click)="onSubmit()"
            class="rounded-xl bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-500 hover:from-emerald-500 hover:to-teal-400 px-6 py-2.5 text-xs font-extrabold text-white shadow-lg shadow-emerald-950/60 transition-all hover:scale-[1.02] active:scale-95"
          >
            Enviar Respostas
          </button>
        </footer>
      </div>
    </div>
  `,
})
export class MicroSurveyModalComponent {
  @Input() isOpen = true;
  @Input() title = 'Pesquisa Pulso Mensal';
  @Output() closed = new EventEmitter<void>();
  @Output() submitted = new EventEmitter<{ q1: number; q2: number; q3: number }>();

  q1Answer = signal<number>(2);
  q2Answer = signal<number>(4);
  q3Answer = signal<number>(5);

  onClose(): void {
    this.closed.emit();
  }

  onSubmit(): void {
    this.submitted.emit({
      q1: this.q1Answer(),
      q2: this.q2Answer(),
      q3: this.q3Answer(),
    });
  }
}
