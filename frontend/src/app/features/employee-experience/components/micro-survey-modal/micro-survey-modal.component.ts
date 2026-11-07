import { Component, Input, Output, EventEmitter, signal } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-micro-survey-modal',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div
      *ngIf="isOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-fadeIn"
    >
      <div class="w-full max-w-lg rounded-2xl bg-[#121118] p-6 shadow-2xl border border-violet-800/50 space-y-5">
        <!-- Header do Modal -->
        <header class="flex items-start justify-between border-b border-zinc-800 pb-4">
          <div class="flex items-center gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-zinc-900 border border-violet-500/40 text-[#8B5CF6] shadow-[0_0_15px_rgba(124,58,237,0.3)]">
              <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div>
              <div class="flex items-center gap-2">
                <h3 class="text-base font-bold text-white">{{ title }}</h3>
                <span class="rounded bg-violet-950 px-2 py-0.5 text-[10px] font-mono font-bold text-violet-300 border border-violet-800/40">
                  Leva 30 segundos
                </span>
              </div>
              <p class="text-xs text-zinc-400 mt-0.5">
                Check-in anônimo mensal de saúde e bem-estar do time (Portaria MTE nº 1.419/2024).
              </p>
            </div>
          </div>

          <button
            type="button"
            (click)="onClose()"
            class="rounded-lg p-1 text-zinc-400 hover:bg-zinc-800 hover:text-white transition-colors"
          >
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </header>

        <!-- Garantia Explícita de Privacidade -->
        <div class="flex items-center gap-2 rounded-xl bg-zinc-900/90 px-3.5 py-2 text-xs text-zinc-200 border border-[#CCFF00]/30 shadow-[0_0_10px_rgba(204,255,0,0.1)] font-mono">
          <span class="h-2 w-2 rounded-full bg-[#CCFF00] shadow-[0_0_6px_#CCFF00] shrink-0"></span>
          <span><strong class="text-[#CCFF00]">100% Anônimo:</strong> Sua resposta é agregada à média da equipe sem identificação de IP ou usuário.</span>
        </div>

        <!-- 3 Perguntas Rápidas com Escala Likert de 1 a 5 -->
        <div class="space-y-4 text-xs text-zinc-300">
          <!-- Pergunta 1 -->
          <div class="rounded-xl border border-zinc-800 bg-zinc-900/60 p-3.5 space-y-2">
            <label class="block font-semibold text-white">
              1. Como você avalia o volume e o ritmo da sua carga de trabalho este mês?
            </label>
            <div class="flex items-center justify-between gap-1 pt-1">
              <button
                *ngFor="let val of [1, 2, 3, 4, 5]"
                type="button"
                (click)="q1Answer.set(val)"
                class="flex-1 rounded-lg py-2 font-mono font-bold transition-all border"
                [ngClass]="q1Answer() === val ? 'bg-[#7C3AED] text-white border-violet-400 shadow-[0_0_12px_rgba(124,58,237,0.4)]' : 'bg-zinc-950 border-zinc-800 text-zinc-400 hover:border-zinc-700 hover:text-white'"
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
          <div class="rounded-xl border border-zinc-800 bg-zinc-900/60 p-3.5 space-y-2">
            <label class="block font-semibold text-white">
              2. Você sente que dispõe do apoio necessário da sua liderança para suas entregas?
            </label>
            <div class="flex items-center justify-between gap-1 pt-1">
              <button
                *ngFor="let val of [1, 2, 3, 4, 5]"
                type="button"
                (click)="q2Answer.set(val)"
                class="flex-1 rounded-lg py-2 font-mono font-bold transition-all border"
                [ngClass]="q2Answer() === val ? 'bg-[#7C3AED] text-white border-violet-400 shadow-[0_0_12px_rgba(124,58,237,0.4)]' : 'bg-zinc-950 border-zinc-800 text-zinc-400 hover:border-zinc-700 hover:text-white'"
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
          <div class="rounded-xl border border-zinc-800 bg-zinc-900/60 p-3.5 space-y-2">
            <label class="block font-semibold text-white">
              3. O ambiente interpessoal do seu time tem sido respeitoso e acolhedor?
            </label>
            <div class="flex items-center justify-between gap-1 pt-1">
              <button
                *ngFor="let val of [1, 2, 3, 4, 5]"
                type="button"
                (click)="q3Answer.set(val)"
                class="flex-1 rounded-lg py-2 font-mono font-bold transition-all border"
                [ngClass]="q3Answer() === val ? 'bg-[#7C3AED] text-white border-violet-400 shadow-[0_0_12px_rgba(124,58,237,0.4)]' : 'bg-zinc-950 border-zinc-800 text-zinc-400 hover:border-zinc-700 hover:text-white'"
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
        <footer class="flex items-center justify-end gap-2.5 pt-3 border-t border-zinc-800">
          <button
            type="button"
            (click)="onClose()"
            class="rounded-xl border border-zinc-700 bg-zinc-900 px-4 py-2 text-xs font-bold text-zinc-300 hover:text-white"
          >
            Pular por Enquanto
          </button>
          <button
            type="button"
            (click)="onSubmit()"
            class="rounded-xl bg-[#CCFF00] px-5 py-2 text-xs font-black text-black hover:bg-[#b8e600] shadow-[0_0_20px_rgba(204,255,0,0.35)]"
          >
            Enviar Respostas Anônimas
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
