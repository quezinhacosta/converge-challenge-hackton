import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { KnowledgeApiService } from './knowledge-api.service';
import {
  CATEGORIAS,
  CategoriaDocumento,
  Documento,
  ROTULO_CATEGORIA,
  ROTULO_STATUS,
  StatusBase,
  erroDaApi,
} from './knowledge.model';
import { KnowledgeDocumentFormComponent } from './components/document-form.component';
import { KnowledgeDocumentDetailComponent } from './components/document-detail.component';
import { KnowledgeSearchTestComponent } from './components/search-test.component';
import { KnowledgePendingListComponent } from './components/pending-list.component';

type Aba = 'documentos' | 'busca' | 'pendencias';

/**
 * Rota /conhecimento: cadastro de documentos para o RAG (nao e cadastro de funcionarios).
 * Para ligar: em app.routes.ts, trocar KnowledgeUnavailableComponent por este componente.
 */
@Component({
  selector: 'app-knowledge-page',
  standalone: true,
  imports: [
    DatePipe,
    FormsModule,
    RouterLink,
    KnowledgeDocumentFormComponent,
    KnowledgeDocumentDetailComponent,
    KnowledgeSearchTestComponent,
    KnowledgePendingListComponent,
  ],
  template: `
    <div class="min-h-screen bg-slate-50/70 font-sans text-slate-900">
      <header class="sticky top-0 z-40 border-b border-slate-200 bg-white">
        <div class="container mx-auto flex flex-wrap items-center justify-between gap-3 px-6 py-3.5">
          <div>
            <a routerLink="/" class="text-xs font-semibold text-indigo-700">← Painel</a>
            <h1 class="text-base font-bold tracking-tight">Base de conhecimento da empresa</h1>
            <p class="text-xs text-slate-500">Políticas, canais e programas que o agente pode citar. Documentos são fonte, nunca instrução.</p>
          </div>
          @if (status(); as s) {
            <div class="flex gap-2 text-xs font-semibold">
              <span class="rounded-full bg-slate-100 px-3 py-1">{{ s.documentos }} documentos</span>
              <span class="rounded-full bg-emerald-50 px-3 py-1 text-emerald-800">{{ s.publicados }} publicados</span>
              @if (s.comErroOuBloqueio) {
                <span class="rounded-full bg-rose-50 px-3 py-1 text-rose-800">{{ s.comErroOuBloqueio }} com erro ou bloqueio</span>
              }
            </div>
          }
        </div>
        <nav class="container mx-auto flex gap-1 px-6" role="tablist">
          @for (a of abas; track a.id) {
            <button role="tab" [attr.aria-selected]="aba() === a.id" (click)="aba.set(a.id)"
              class="border-b-2 px-3 py-2 text-sm font-semibold"
              [class]="aba() === a.id ? 'border-indigo-600 text-indigo-700' : 'border-transparent text-slate-500 hover:text-slate-800'">
              {{ a.rotulo }}
            </button>
          }
        </nav>
      </header>

      <main class="container mx-auto px-6 py-6">
        @if (erroGeral(); as e) {
          <p role="alert" class="mb-4 rounded-lg bg-rose-50 p-3 text-sm text-rose-900">{{ e }}</p>
        }

        @switch (aba()) {
          @case ('documentos') {
            <div class="grid gap-6 lg:grid-cols-[minmax(0,2fr)_minmax(0,3fr)]">
              <section class="rounded-xl border border-slate-200 bg-white p-4">
                <div class="mb-3 flex flex-wrap items-center gap-2">
                  <select [(ngModel)]="filtro" (ngModelChange)="carregar()" aria-label="Filtrar por categoria"
                    class="rounded-lg border border-slate-300 bg-white px-2 py-1.5 text-sm">
                    <option value="">Todas as categorias</option>
                    @for (c of categorias; track c.valor) { <option [value]="c.valor">{{ c.rotulo }}</option> }
                  </select>
                  <button class="ml-auto rounded-lg bg-indigo-600 px-3 py-1.5 text-sm font-bold text-white" (click)="novo()">Novo documento</button>
                </div>
                @if (carregando()) { <p class="text-sm text-slate-500">Carregando…</p> }
                @if (!carregando() && !documentos().length) {
                  <p class="rounded-lg bg-slate-50 p-4 text-sm text-slate-600">
                    Nenhum documento ainda. Comece pelo canal de apoio psicológico e pela política de saúde emocional:
                    são o que o agente mais precisa para sugerir ações reais da empresa.
                  </p>
                }
                <ul class="divide-y divide-slate-100">
                  @for (d of documentos(); track d.id) {
                    <li>
                      <button class="w-full px-2 py-2.5 text-left hover:bg-slate-50" [class.bg-indigo-50]="selecionado()?.id === d.id" (click)="selecionar(d)">
                        <span class="block text-sm font-semibold">{{ d.titulo }}</span>
                        <span class="block text-xs text-slate-500">
                          {{ rotuloCategoria[d.categoria] }} ·
                          @if (d.versaoPublicada) { publicado {{ d.versaoPublicada.rotulo }} } @else { não publicado }
                          @if (ultimoStatus(d); as st) { @if (st !== 'PRONTO' && st !== 'SUBSTITUIDA') { · {{ rotuloStatus[st] }} } }
                          · atualizado {{ d.atualizadoEm | date: 'dd/MM/yyyy' }}
                        </span>
                      </button>
                    </li>
                  }
                </ul>
              </section>

              <section class="rounded-xl border border-slate-200 bg-white p-4">
                @if (criando()) {
                  <h2 class="mb-3 text-lg font-bold">Novo documento</h2>
                  <app-knowledge-document-form (salvo)="aoCriar($event)" (cancelado)="criando.set(false)" />
                } @else if (selecionado()) {
                  <app-knowledge-document-detail [doc]="selecionado()!" (alterado)="aoAlterar($event)" (excluido)="aoExcluir($event)" />
                } @else {
                  <p class="text-sm text-slate-500">Escolha um documento na lista ou cadastre um novo.</p>
                }
              </section>
            </div>
          }
          @case ('busca') {
            <section class="rounded-xl border border-slate-200 bg-white p-4"><app-knowledge-search-test /></section>
          }
          @case ('pendencias') {
            <section class="rounded-xl border border-slate-200 bg-white p-4">
              <app-knowledge-pending-list (abrir)="abrirDocumento($event)" />
            </section>
          }
        }
      </main>
    </div>
  `,
})
export class KnowledgePageComponent implements OnInit {
  private readonly api = inject(KnowledgeApiService);

  readonly abas: { id: Aba; rotulo: string }[] = [
    { id: 'documentos', rotulo: 'Documentos' },
    { id: 'busca', rotulo: 'Testar busca' },
    { id: 'pendencias', rotulo: 'Pendências' },
  ];
  readonly categorias = CATEGORIAS;
  readonly rotuloCategoria = ROTULO_CATEGORIA;
  readonly rotuloStatus = ROTULO_STATUS;

  readonly aba = signal<Aba>('documentos');
  readonly documentos = signal<Documento[]>([]);
  readonly selecionadoId = signal<string | null>(null);
  readonly selecionado = computed(() => this.documentos().find(d => d.id === this.selecionadoId()) ?? null);
  readonly criando = signal(false);
  readonly carregando = signal(true);
  readonly status = signal<StatusBase | null>(null);
  readonly erroGeral = signal<string | null>(null);
  filtro: CategoriaDocumento | '' = '';

  ngOnInit(): void {
    this.carregar();
  }

  carregar(): void {
    this.carregando.set(true);
    this.api.listar(this.filtro || undefined).subscribe({
      next: docs => {
        this.carregando.set(false);
        this.erroGeral.set(null);
        this.documentos.set(docs);
      },
      error: err => {
        this.carregando.set(false);
        this.erroGeral.set(erroDaApi(err).mensagem);
      },
    });
    this.api.status().subscribe({ next: s => this.status.set(s), error: () => this.status.set(null) });
  }

  ultimoStatus(d: Documento) {
    const ultima = [...d.versoes].sort((a, b) => b.numero - a.numero)[0];
    return ultima?.status ?? null;
  }

  novo(): void {
    this.selecionadoId.set(null);
    this.criando.set(true);
  }

  selecionar(d: Documento): void {
    this.criando.set(false);
    this.selecionadoId.set(d.id);
  }

  abrirDocumento(id: string): void {
    this.aba.set('documentos');
    this.criando.set(false);
    this.selecionadoId.set(id);
  }

  aoCriar(doc: Documento): void {
    this.criando.set(false);
    this.substituir(doc);
    this.selecionadoId.set(doc.id);
  }

  aoAlterar(doc: Documento): void {
    this.substituir(doc);
  }

  aoExcluir(id: string): void {
    this.documentos.update(lista => lista.filter(d => d.id !== id));
    this.selecionadoId.set(null);
    this.carregar();
  }

  private substituir(doc: Documento): void {
    this.documentos.update(lista => [doc, ...lista.filter(d => d.id !== doc.id)]);
    this.api.status().subscribe({ next: s => this.status.set(s), error: () => undefined });
  }
}
