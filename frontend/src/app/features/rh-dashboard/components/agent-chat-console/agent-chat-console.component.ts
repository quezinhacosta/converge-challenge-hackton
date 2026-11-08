import { Component, Output, EventEmitter, inject, signal, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PulsoApiService, ChatResponse } from '../../../../core/services/pulso-api.service';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'pulso';
  text: string;
  timestamp: string;
  isRefusal?: boolean;
  refusalReason?: string;
  sourcesUsed?: string[];
  suggestedAction?: string;
}

@Component({
  selector: 'app-agent-chat-console',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="flex h-[620px] flex-col overflow-hidden rounded-2xl border border-slate-200/90 bg-white shadow-sm">
      <!-- Header do Copilot -->
      <header class="flex items-center justify-between border-b border-slate-100 bg-slate-50/80 px-5 py-3.5">
        <div class="flex items-center gap-2.5">
          <div class="flex h-8 w-8 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-xs">
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
            </svg>
          </div>
          <div>
            <h3 class="text-sm font-bold text-slate-900 flex items-center gap-1.5">
              Assistente do RH
              <span class="inline-flex items-center rounded-full bg-emerald-100 px-2 py-0.2 text-[10px] font-semibold text-emerald-800">
                VytAI
              </span>
            </h3>
            <p class="text-[11px] text-slate-500">
              Indicadores agregados e ações para revisão do RH
            </p>
          </div>
        </div>

        <button
          type="button"
          (click)="clearHistory()"
          class="rounded-lg p-1.5 text-xs text-slate-400 hover:bg-slate-200/60 hover:text-slate-600 transition-colors"
          title="Limpar histórico do chat"
        >
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
          </svg>
        </button>
      </header>

      <!-- Chips de Sugestões Rápidas (Pitch Demos) -->
      <div class="border-b border-slate-100 bg-white px-4 py-2">
        <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1.5">
          Por onde começar
        </span>
        <div class="flex flex-wrap gap-1.5">
          <button
            *ngFor="let chip of quickChips"
            type="button"
            (click)="selectChip(chip.query)"
            class="rounded-full border border-slate-200 bg-slate-50 px-2.5 py-1 text-[11px] font-medium text-slate-700 hover:border-indigo-300 hover:bg-indigo-50 hover:text-indigo-700 transition-colors"
          >
            {{ chip.label }}
          </button>
        </div>
      </div>

      <!-- Área de Mensagens com Scroll -->
      <div #messagesContainer class="flex-1 space-y-4 overflow-y-auto p-4 bg-slate-50/30">
        <!-- Boas-vindas -->
        <div *ngIf="messages.length === 0" class="my-6 text-center text-slate-500 space-y-2">
          <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
            </svg>
          </div>
          <p class="text-xs font-semibold text-slate-700">Como posso ajudar o RH hoje?</p>
          <p class="text-[11px] text-slate-500 max-w-sm mx-auto">
            Consulte os indicadores disponíveis, organize acompanhamentos e prepare ações para aprovação.
          </p>
        </div>

        <!-- Lista de Mensagens -->
        <div
          *ngFor="let msg of messages"
          class="flex flex-col"
          [ngClass]="msg.sender === 'user' ? 'items-end' : 'items-start'"
        >
          <!-- Mensagem do Usuário -->
          <div
            *ngIf="msg.sender === 'user'"
            class="max-w-[85%] rounded-2xl rounded-tr-sm bg-indigo-600 px-4 py-2.5 text-xs text-white shadow-xs"
          >
            <p class="leading-relaxed">{{ msg.text }}</p>
            <span class="mt-1 block text-right text-[10px] text-indigo-200 font-mono">{{ msg.timestamp }}</span>
          </div>

          <!-- Mensagem do VytAI: Caso Bloqueado por Guardrail Ético / LGPD -->
          <div
            *ngIf="msg.sender === 'pulso' && msg.isRefusal"
            class="max-w-[90%] rounded-2xl rounded-tl-sm border border-amber-300 bg-amber-50/80 p-4 shadow-xs space-y-2"
          >
            <div class="flex items-center gap-2">
              <div class="flex h-6 w-6 items-center justify-center rounded-lg bg-amber-500 text-white shadow-xs">
                <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                </svg>
              </div>
              <span class="inline-flex items-center rounded-full bg-amber-200/80 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-amber-900">
                Consulta protegida
              </span>
            </div>

            <p class="text-xs text-amber-950 font-medium leading-relaxed">
              {{ msg.text }}
            </p>

            <div class="rounded-lg border border-amber-200 bg-white/70 p-2.5 text-[11px] text-amber-900 space-y-1">
              <div class="font-bold flex items-center gap-1">
                <svg class="h-3.5 w-3.5 text-amber-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
                </svg>
                Proteção de privacidade
              </div>
              <p class="text-slate-600">
                {{ msg.refusalReason || 'Proteção de dados sensíveis de saúde e vedação estrita a buscas individualizadas de colaboradores.' }}
              </p>
              <p class="text-indigo-800 font-medium pt-1" *ngIf="msg.suggestedAction">
                Orientação: {{ msg.suggestedAction }}
              </p>
            </div>

            <div class="flex items-center justify-between text-[10px] text-amber-800/70 pt-1">
              <span>Fontes: {{ (msg.sourcesUsed || ['guardrail_lgpd']).join(', ') }}</span>
              <span class="font-mono">{{ msg.timestamp }}</span>
            </div>
          </div>

          <!-- Mensagem do VytAI: Resposta Normal / Corporativa -->
          <div
            *ngIf="msg.sender === 'pulso' && !msg.isRefusal"
            class="max-w-[90%] rounded-2xl rounded-tl-sm border border-slate-200/90 bg-white p-4 shadow-xs space-y-2"
          >
            <div class="flex items-center gap-2">
              <div class="flex h-5 w-5 items-center justify-center rounded-md bg-indigo-100 text-indigo-700">
                <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                </svg>
              </div>
              <span class="text-[11px] font-bold text-slate-800">Assistente VytAI</span>
            </div>

            <p class="text-xs text-slate-700 leading-relaxed whitespace-pre-line">
              {{ msg.text }}
            </p>

            <div *ngIf="msg.suggestedAction" class="rounded-lg bg-indigo-50/70 p-2 text-[11px] text-indigo-900 border border-indigo-100">
              <span class="font-bold">Ação Sugerida:</span> {{ msg.suggestedAction }}
            </div>

            <div class="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-slate-100">
              <span>Fontes informadas: {{ (msg.sourcesUsed || []).join(', ') || 'Não informadas' }}</span>
              <span class="font-mono">{{ msg.timestamp }}</span>
            </div>
          </div>
        </div>

        <!-- Indicador de Carregamento / Digitação -->
        <div *ngIf="loading" class="flex items-center gap-2 text-xs text-slate-400 italic py-2 pl-2">
          <div class="flex space-x-1">
            <div class="h-2 w-2 rounded-full bg-indigo-400 animate-bounce"></div>
            <div class="h-2 w-2 rounded-full bg-indigo-400 animate-bounce [animation-delay:0.2s]"></div>
            <div class="h-2 w-2 rounded-full bg-indigo-400 animate-bounce [animation-delay:0.4s]"></div>
          </div>
          <span>VytAI consultando as informações disponíveis...</span>
        </div>
      </div>

      <!-- Barra de Input com Botão de Envio -->
      <form (ngSubmit)="handleSend()" class="border-t border-slate-100 bg-white p-3 flex items-center gap-2">
        <input
          type="text"
          [(ngModel)]="inputQuery"
          name="query"
          placeholder="O que o RH precisa acompanhar hoje?"
          class="flex-1 rounded-xl border border-slate-300 bg-slate-50/60 px-3.5 py-2.5 text-xs text-slate-900 placeholder-slate-400 focus:border-indigo-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-100 transition-all"
        />
        <button
          type="submit"
          [disabled]="loading || !inputQuery.trim()"
          class="inline-flex items-center justify-center rounded-xl bg-indigo-600 px-4 py-2.5 text-xs font-bold text-white shadow-xs hover:bg-indigo-700 active:scale-95 disabled:opacity-40 disabled:pointer-events-none transition-all"
        >
          <span>Enviar</span>
          <svg class="h-3.5 w-3.5 ml-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/>
          </svg>
        </button>
      </form>
    </div>
  `,
})
export class AgentChatConsoleComponent implements AfterViewChecked {
  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;
  @Output() querySubmit = new EventEmitter<string>();

  private readonly pulsoApi = inject(PulsoApiService);

  messages: ChatMessage[] = [];
  inputQuery = '';
  loading = false;

  quickChips = [
    { label: 'Visão dos setores', query: 'Resuma os indicadores agregados disponíveis por setor e informe suas limitações.' },
    { label: 'Pendências do RH', query: 'Consulte minhas pendências de acompanhamento de RH.' },
    { label: 'Planejar acompanhamento', query: 'Quero preparar uma intervenção. Quais informações você precisa antes de criar a proposta?' },
  ];

  ngAfterViewChecked(): void {
    this.scrollToBottom();
  }

  selectChip(query: string): void {
    this.inputQuery = query;
    this.handleSend();
  }

  handleSend(): void {
    const text = this.inputQuery.trim();
    if (!text || this.loading) return;

    const time = new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });

    this.messages.push({
      id: String(Date.now()),
      sender: 'user',
      text,
      timestamp: time,
    });

    this.inputQuery = '';
    this.loading = true;
    this.querySubmit.emit(text);

    this.pulsoApi.sendChatQuery(text).subscribe({
      next: (res: ChatResponse) => {
        this.loading = false;
        this.messages.push({
          id: String(Date.now() + 1),
          sender: 'pulso',
          text: res.replyText,
          timestamp: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }),
          isRefusal: res.isRefusal,
          refusalReason: res.refusalReason,
          sourcesUsed: res.sourcesUsed,
          suggestedAction: res.suggestedAction,
        });
      },
      error: () => {
        this.loading = false;
        this.messages.push({id: crypto.randomUUID(), sender: 'pulso', text: 'Não foi possível consultar o assistente. Verifique sua sessão e tente novamente.', timestamp: new Date().toLocaleTimeString('pt-BR', {hour:'2-digit',minute:'2-digit'})});
      },
    });
  }

  clearHistory(): void {
    this.messages = [];
  }

  private scrollToBottom(): void {
    try {
      if (this.messagesContainer) {
        this.messagesContainer.nativeElement.scrollTop = this.messagesContainer.nativeElement.scrollHeight;
      }
    } catch {
      // Ignora falhas de scroll
    }
  }
}
