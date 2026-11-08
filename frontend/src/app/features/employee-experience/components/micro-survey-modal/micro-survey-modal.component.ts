import { Component, Input, Output, EventEmitter, signal } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-micro-survey-modal',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div
      *ngIf="isOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-xs p-4"
    >
      <div class="w-full max-w-lg rounded-xl bg-zinc-900 p-6 border border-zinc-800 space-y-5">
        <!-- Header do Modal -->
        <header class="flex items-start justify-between border-b border-zinc-800 pb-3">
          <div class="flex items-center gap-2.5">
            <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-zinc-800 text-zinc-300">
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div>
              <div class="flex items-center gap-2">
                <h3 class="text-base font-semibold text-white">{{ title }}</h3>
                <span class="rounded bg-zinc-800 px-1.5 py-0.2 text-[10px] font-mono text-zinc-400 border border-zinc-700">
                  Leva 30 segundos
                </span>
              </div>
              <p class="text-xs text-zinc-400 mt-0.5">
                Check-in anônimo de bem-estar da equipe (Portaria MTE nº 1.419/2024).
              </p>
            </div>
          </div>

          <button
            type="button"
            (click)="onClose()"
            class="text-zinc-400 hover:text-white p-1"
          >
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </header>

        <!-- Garantia de Anonimato -->
        <div class="rounded-lg bg-zinc-950 p-2.5 text-xs text-zinc-400 border border-zinc-800 font-mono">
          <strong class="text-zinc-200">100% Anônimo:</strong> Sua resposta é agregada à média do setor sem identificação individual ou de IP.
        </div>

        <!-- 3 Perguntas Rápidas -->
        <div class="space-y-3.5 text-xs text-zinc-300">
          <!-- Pergunta 1 -->
          <div class="rounded-lg border border-zinc-800 bg-zinc-950 p-3.5 space-y-2">
            <label class="block font-medium text-white">
              1. Como você avalia o volume e o ritmo da sua carga de trabalho este mês?
            </label>
            <div class="flex items-center justify-between gap-1 pt-1">
              <button
                *ngFor="let val of [1, 2, 3, 4, 5]"
                type="button"
                (click)="q1Answer.set(val)"
                class="flex-1 rounded py-1.5 font-mono font-medium transition-colors border"
                [ngClass]="q1Answer() === val ? 'bg-zinc-200 text-black border-zinc-200 font-bold' : 'bg-zinc-900 border-zinc-800 text-zinc-400 hover:border-zinc-700 hover:text-white'"
              >
                {{ val }}
              </button>
            </div>
            <div class="flex justify-between text-[10px] text-zinc-500 font-mono">
              <span>Muito Pesada (1)</span>
              <span>Equilibrada (5)</span>
            </div>
          </div>

          <!-- Pergunta 2 -->
          <div class="rounded-lg border border-zinc-800 bg-zinc-950 p-3.5 space-y-2">
            <label class="block font-medium text-white">
              2. Você sente que dispõe do apoio necessário da sua liderança para suas entregas?
            </label>
            <div class="flex items-center justify-between gap-1 pt-1">
              <button
                *ngFor="let val of [1, 2, 3, 4, 5]"
                type="button"
                (click)="q2Answer.set(val)"
                class="flex-1 rounded py-1.5 font-mono font-medium transition-colors border"
                [ngClass]="q2Answer() === val ? 'bg-zinc-200 text-black border-zinc-200 font-bold' : 'bg-zinc-900 border-zinc-800 text-zinc-400 hover:border-zinc-700 hover:text-white'"
              >
                {{ val }}
              </button>
            </div>
            <div class="flex justify-between text-[10px] text-zinc-500 font-mono">
              <span>Pouco Apoio (1)</span>
              <span>Total Apoio (5)</span>
            </div>
          </div>

          <!-- Pergunta 3 -->
          <div class="rounded-lg border border-zinc-800 bg-zinc-950 p-3.5 space-y-2">
            <label class="block font-medium text-white">
              3. O ambiente interpessoal do seu time tem sido respeitoso e acolhedor?
            </label>
            <div class="flex items-center justify-between gap-1 pt-1">
              <button
                *ngFor="let val of [1, 2, 3, 4, 5]"
                type="button"
                (click)="q3Answer.set(val)"
                class="flex-1 rounded py-1.5 font-mono font-medium transition-colors border"
                [ngClass]="q3Answer() === val ? 'bg-zinc-200 text-black border-zinc-200 font-bold' : 'bg-zinc-900 border-zinc-800 text-zinc-400 hover:border-zinc-700 hover:text-white'"
              >
                {{ val }}
              </button>
            </div>
            <div class="flex justify-between text-[10px] text-zinc-500 font-mono">
              <span>Conflituoso (1)</span>
              <span>Harmonioso (5)</span>
            </div>
          </div>
        </div>

        <!-- Footer com Ação -->
        <footer class="flex items-center justify-end gap-2 pt-3 border-t border-zinc-800">
          <button
            type="button"
            (click)="onClose()"
            class="rounded-lg border border-zinc-700 bg-zinc-800 hover:bg-zinc-700 px-3.5 py-1.5 text-xs font-medium text-zinc-300"
          >
            Cancelar
          </button>
          <button
            type="button"
            (click)="onSubmit()"
            class="rounded-lg bg-emerald-600 hover:bg-emerald-500 px-4 py-1.5 text-xs font-medium text-white transition-colors"
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
