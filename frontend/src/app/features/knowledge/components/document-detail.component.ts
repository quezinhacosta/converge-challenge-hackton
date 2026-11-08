import { Component, EventEmitter, Input, Output, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { Observable } from 'rxjs';
import { KnowledgeApiService } from '../knowledge-api.service';
import { Documento, ROTULO_CATEGORIA, ROTULO_STATUS, StatusVersao, Versao, erroDaApi } from '../knowledge.model';
import { KnowledgeDocumentFormComponent } from './document-form.component';

const COR_STATUS: Record<StatusVersao, string> = {
  RECEBIDO: 'bg-slate-100 text-slate-700',
  PROCESSANDO: 'bg-sky-100 text-sky-800',
  PRONTO: 'bg-emerald-100 text-emerald-800',
  ERRO: 'bg-rose-100 text-rose-800',
  BLOQUEADO: 'bg-amber-100 text-amber-900',
  SUBSTITUIDA: 'bg-slate-100 text-slate-500',
};

/** Detalhe do documento: versoes, status, publicacao e exclusao efetiva. */
@Component({
  selector: 'app-knowledge-document-detail',
  standalone: true,
  imports: [DatePipe, KnowledgeDocumentFormComponent],
  template: `
    <article class="space-y-5">
      <header class="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p class="text-xs font-bold uppercase tracking-wider text-indigo-700">{{ rotuloCategoria[doc.categoria] }}</p>
          <h2 class="text-lg font-bold text-slate-900">{{ doc.titulo }}</h2>
          <p class="text-sm text-slate-600">Responsável: {{ doc.responsavel }} @if (doc.fonte) { · Fonte: {{ doc.fonte }} }</p>
        </div>
        @if (doc.versaoPublicada; as pub) {
          <span class="rounded-full bg-emerald-50 px-3 py-1 text-xs font-bold text-emerald-800 ring-1 ring-emerald-200">
            Publicado: {{ pub.rotulo }} — o agente usa esta versão
          </span>
        } @else {
          <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-700">Não publicado — o agente não usa</span>
        }
      </header>

      @if (erro(); as e) { <p role="alert" class="rounded-lg bg-rose-50 p-3 text-sm text-rose-900">{{ e }}</p> }

      <section>
        <h3 class="mb-2 text-sm font-bold text-slate-800">Versões</h3>
        <ul class="divide-y divide-slate-100 rounded-lg border border-slate-200">
          @for (v of versoesRecentes(); track v.id) {
            <li class="p-3 text-sm">
              <div class="flex flex-wrap items-center gap-2">
                <span class="font-semibold">{{ v.rotulo }}</span>
                <span class="rounded px-2 py-0.5 text-xs font-bold" [class]="corStatus[v.status]">{{ rotuloStatus[v.status] }}</span>
                @if (v.publicada) { <span class="rounded bg-indigo-600 px-2 py-0.5 text-xs font-bold text-white">Publicada</span> }
                <span class="text-xs text-slate-500">
                  {{ v.origem === 'UPLOAD' ? (v.nomeArquivo || 'arquivo') : 'texto colado' }} ·
                  vale de {{ v.vigenciaInicio | date: 'dd/MM/yyyy' }}{{ v.vigenciaFim ? ' até ' + (v.vigenciaFim | date: 'dd/MM/yyyy') : '' }}
                  @if (v.status === 'PRONTO') { · {{ v.quantidadeTrechos }} trechos }
                </span>
                <span class="ml-auto flex gap-1">
                  @if (v.status === 'PRONTO' && !v.publicada) {
                    <button class="rounded-md bg-indigo-600 px-2.5 py-1 text-xs font-bold text-white disabled:opacity-50"
                      [disabled]="ocupado()" (click)="executar(api.publicar(v.id))">Publicar</button>
                  }
                  @if (v.publicada) {
                    <button class="rounded-md px-2.5 py-1 text-xs font-bold text-slate-700 ring-1 ring-slate-300 disabled:opacity-50"
                      [disabled]="ocupado()" (click)="executar(api.despublicar(v.id))">Despublicar</button>
                  }
                  @if (v.status === 'ERRO') {
                    <button class="rounded-md px-2.5 py-1 text-xs font-bold text-slate-700 ring-1 ring-slate-300 disabled:opacity-50"
                      [disabled]="ocupado()" (click)="reprocessar(v)">Reprocessar</button>
                  }
                </span>
              </div>
              @if (v.status === 'ERRO' || v.status === 'BLOQUEADO') {
                <p class="mt-1 text-xs" [class]="v.status === 'BLOQUEADO' ? 'text-amber-900' : 'text-rose-800'">
                  {{ v.erroMensagem }}
                  @if (v.status === 'BLOQUEADO') { O original foi apagado. Remova os dados e envie uma nova versão. }
                </p>
              }
            </li>
          }
        </ul>
      </section>

      @if (novaVersao()) {
        <section class="rounded-lg border border-slate-200 p-4">
          <h3 class="mb-3 text-sm font-bold text-slate-800">Nova versão</h3>
          <p class="mb-3 text-xs text-slate-600">A versão atual continua valendo até você publicar a nova.</p>
          <app-knowledge-document-form [documentoId]="doc.id" (salvo)="aoSalvarVersao($event)" (cancelado)="novaVersao.set(false)" />
        </section>
      } @else {
        <div class="flex flex-wrap gap-2">
          <button class="rounded-lg px-3 py-2 text-sm font-semibold text-indigo-700 ring-1 ring-indigo-200" (click)="novaVersao.set(true)">
            Substituir por nova versão
          </button>
          @if (!confirmandoExclusao()) {
            <button class="rounded-lg px-3 py-2 text-sm font-semibold text-rose-700" (click)="confirmandoExclusao.set(true)">Excluir documento</button>
          } @else {
            <span class="flex items-center gap-2 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-900" role="alert">
              Excluir apaga o original, todas as versões e trechos, e não pode ser desfeito.
              <button class="rounded-md bg-rose-600 px-2.5 py-1 text-xs font-bold text-white disabled:opacity-50" [disabled]="ocupado()" (click)="excluir()">Excluir de vez</button>
              <button class="text-xs font-semibold" (click)="confirmandoExclusao.set(false)">Cancelar</button>
            </span>
          }
        </div>
      }
    </article>
  `,
})
export class KnowledgeDocumentDetailComponent {
  readonly api = inject(KnowledgeApiService);

  @Input({ required: true }) doc!: Documento;
  @Output() alterado = new EventEmitter<Documento>();
  @Output() excluido = new EventEmitter<string>();

  readonly rotuloCategoria = ROTULO_CATEGORIA;
  readonly rotuloStatus = ROTULO_STATUS;
  readonly corStatus = COR_STATUS;
  readonly ocupado = signal(false);
  readonly erro = signal<string | null>(null);
  readonly novaVersao = signal(false);
  readonly confirmandoExclusao = signal(false);

  versoesRecentes(): Versao[] {
    return [...this.doc.versoes].sort((a, b) => b.numero - a.numero);
  }

  executar(pedido: Observable<Documento>): void {
    this.ocupado.set(true);
    this.erro.set(null);
    pedido.subscribe({
      next: doc => {
        this.ocupado.set(false);
        this.alterado.emit(doc);
      },
      error: err => {
        this.ocupado.set(false);
        this.erro.set(erroDaApi(err).mensagem);
      },
    });
  }

  reprocessar(v: Versao): void {
    this.ocupado.set(true);
    this.api.reprocessar(v.id).subscribe({
      next: () => this.executar(this.api.obter(this.doc.id)),
      error: err => {
        this.ocupado.set(false);
        this.erro.set(erroDaApi(err).mensagem);
      },
    });
  }

  aoSalvarVersao(doc: Documento): void {
    this.novaVersao.set(false);
    this.alterado.emit(doc);
  }

  excluir(): void {
    this.ocupado.set(true);
    this.api.excluir(this.doc.id).subscribe({
      next: () => {
        this.ocupado.set(false);
        this.excluido.emit(this.doc.id);
      },
      error: err => {
        this.ocupado.set(false);
        this.erro.set(erroDaApi(err).mensagem);
      },
    });
  }
}
