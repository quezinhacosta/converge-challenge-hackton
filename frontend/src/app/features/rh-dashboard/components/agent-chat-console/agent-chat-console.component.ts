import { Component, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'pulso';
  text: string;
  isRefusal?: boolean;
}

@Component({
  selector: 'app-agent-chat-console',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="flex h-[450px] flex-col rounded-xl border border-slate-200 bg-white shadow-sm">
      <div class="border-b border-slate-200 p-4">
        <h3 class="font-bold text-slate-800">Assistente Pulso (NR-1)</h3>
        <p class="text-xs text-slate-500">
          Análise contínua de riscos psicossociais por áreas e times corporativos.
        </p>
      </div>

      <div class="flex-1 space-y-3 overflow-y-auto p-4">
        <div
          *ngFor="let msg of messages"
          class="flex"
          [ngClass]="msg.sender === 'user' ? 'justify-end' : 'justify-start'"
        >
          <div
            class="max-w-[80%] rounded-lg p-3 text-sm"
            [ngClass]="{
              'bg-indigo-600 text-white': msg.sender === 'user',
              'border border-amber-300 bg-amber-50 text-amber-900':
                msg.sender === 'pulso' && msg.isRefusal,
              'bg-slate-100 text-slate-800': msg.sender === 'pulso' && !msg.isRefusal
            }"
          >
            {{ msg.text }}
          </div>
        </div>
      </div>

      <form (ngSubmit)="handleSend()" class="border-t border-slate-200 p-3 flex gap-2">
        <input
          type="text"
          [(ngModel)]="inputQuery"
          name="query"
          placeholder="Ex: Como está o time de Logística? ou teste: Me mostra os atestados da Carla"
          class="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <button
          type="submit"
          [disabled]="loading"
          class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
        >
          Enviar
        </button>
      </form>
    </div>
  `,
})
export class AgentChatConsoleComponent {
  @Output() querySubmit = new EventEmitter<string>();

  messages: ChatMessage[] = [];
  inputQuery = '';
  loading = false;

  handleSend(): void {
    if (!this.inputQuery.trim() || this.loading) return;

    const userText = this.inputQuery;
    this.inputQuery = '';
    this.messages.push({
      id: String(Date.now()),
      sender: 'user',
      text: userText,
    });

    this.loading = true;

    // Simulação e acionamento dos guardrails
    if (userText.toLowerCase().includes('carla')) {
      setTimeout(() => {
        this.messages.push({
          id: String(Date.now() + 1),
          sender: 'pulso',
          text: 'O Pulso opera exclusivamente no nível de áreas e times para gestão de riscos da NR-1. Em conformidade com a LGPD e as diretrizes éticas do Desafio Tako, informações individuais de saúde ou desempenho não são consultadas nem exibidas.',
          isRefusal: true,
        });
        this.loading = false;
      }, 500);
    } else {
      setTimeout(() => {
        this.messages.push({
          id: String(Date.now() + 1),
          sender: 'pulso',
          text: 'O time de Logística apresenta estabilidade operacional no ponto e folha, com sinal amarelo recente decorrente de troca de liderança em setembro.',
          isRefusal: false,
        });
        this.loading = false;
      }, 600);
    }
  }
}
