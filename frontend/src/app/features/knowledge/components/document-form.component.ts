import { Component, EventEmitter, Input, Output, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { KnowledgeApiService } from '../knowledge-api.service';
import { CATEGORIAS, CategoriaDocumento, Documento, erroDaApi } from '../knowledge.model';

const LIMITE_BYTES = 10 * 1024 * 1024;
const EXTENSOES = ['.pdf', '.txt', '.md'];

/**
 * Cadastro de documento (modo "novo") ou de nova versao (modo "versao", com documentoId).
 * O processamento e a triagem de dados sensiveis acontecem no servidor; aqui so orientamos.
 */
@Component({
  selector: 'app-knowledge-document-form',
  standalone: true,
  imports: [FormsModule],
  template: `
    <form class="space-y-4" (ngSubmit)="enviar()" #f="ngForm">
      <div class="flex gap-1 rounded-lg bg-slate-100 p-1 w-fit" role="tablist">
        <button type="button" role="tab" [attr.aria-selected]="origem() === 'texto'"
          class="rounded-md px-3 py-1.5 text-sm font-semibold"
          [class]="origem() === 'texto' ? 'bg-white shadow-sm text-slate-900' : 'text-slate-600'"
          (click)="origem.set('texto')">Colar texto</button>
        <button type="button" role="tab" [attr.aria-selected]="origem() === 'arquivo'"
          class="rounded-md px-3 py-1.5 text-sm font-semibold"
          [class]="origem() === 'arquivo' ? 'bg-white shadow-sm text-slate-900' : 'text-slate-600'"
          (click)="origem.set('arquivo')">Enviar arquivo</button>
      </div>

      @if (!documentoId) {
        <div class="grid gap-4 sm:grid-cols-2">
          <label class="block sm:col-span-2">
            <span class="text-sm font-semibold text-slate-700">Título</span>
            <input name="titulo" [(ngModel)]="titulo" required minlength="3" maxlength="200"
              class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" placeholder="Ex.: Política de saúde emocional" />
          </label>
          <label class="block">
            <span class="text-sm font-semibold text-slate-700">Categoria</span>
            <select name="categoria" [(ngModel)]="categoria" required
              class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm bg-white">
              @for (c of categorias; track c.valor) { <option [value]="c.valor">{{ c.rotulo }}</option> }
            </select>
            <span class="mt-1 block text-xs text-slate-500">{{ ajudaCategoria() }}</span>
          </label>
          <label class="block">
            <span class="text-sm font-semibold text-slate-700">Responsável</span>
            <input name="responsavel" [(ngModel)]="responsavel" required minlength="2" maxlength="120"
              class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" placeholder="Área ou cargo, não o nome de colaborador" />
          </label>
          <label class="block sm:col-span-2">
            <span class="text-sm font-semibold text-slate-700">Fonte <span class="font-normal text-slate-500">(opcional)</span></span>
            <input name="fonte" [(ngModel)]="fonte" maxlength="200"
              class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" placeholder="Ex.: Intranet > RH > Políticas" />
          </label>
        </div>
      }

      <div class="grid gap-4 sm:grid-cols-3">
        <label class="block">
          <span class="text-sm font-semibold text-slate-700">Versão <span class="font-normal text-slate-500">(opcional)</span></span>
          <input name="rotulo" [(ngModel)]="rotuloVersao" maxlength="60"
            class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" placeholder="Ex.: 2026.1" />
        </label>
        <label class="block">
          <span class="text-sm font-semibold text-slate-700">Vale a partir de</span>
          <input type="date" name="inicio" [(ngModel)]="vigenciaInicio"
            class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" />
        </label>
        <label class="block">
          <span class="text-sm font-semibold text-slate-700">Vale até <span class="font-normal text-slate-500">(opcional)</span></span>
          <input type="date" name="fim" [(ngModel)]="vigenciaFim"
            class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" />
        </label>
      </div>

      @if (origem() === 'texto') {
        <label class="block">
          <span class="text-sm font-semibold text-slate-700">Conteúdo</span>
          <textarea name="texto" [(ngModel)]="texto" rows="10" maxlength="500000"
            class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 font-mono text-sm"
            placeholder="Cole aqui o texto do documento. Títulos com # ajudam a dividir em seções."></textarea>
          <span class="text-xs text-slate-500">{{ texto.length.toLocaleString('pt-BR') }} / 500.000 caracteres</span>
        </label>
      } @else {
        <div class="rounded-lg border-2 border-dashed border-slate-300 p-4">
          <input type="file" accept=".pdf,.txt,.md" (change)="escolher($event)" class="text-sm"
            aria-label="Arquivo .pdf, .txt ou .md" />
          <p class="mt-2 text-xs text-slate-500">PDF com texto selecionável, .txt ou .md, até 10 MB. PDF escaneado não é lido (sem OCR).</p>
          @if (arquivo(); as a) {
            <p class="mt-1 text-sm text-slate-700">{{ a.name }} · {{ (a.size / 1024).toFixed(0) }} KB</p>
          }
        </div>
      }

      <label class="flex items-start gap-2 rounded-lg bg-amber-50 p-3 text-sm text-amber-950">
        <input type="checkbox" name="confirma" [(ngModel)]="confirma" class="mt-0.5" />
        <span>Confirmo que o documento <strong>não contém</strong> dados pessoais sensíveis, como atestados,
          laudos, CID, CPF ou nomes de colaboradores ligados a saúde. Se contiver, o sistema bloqueia e apaga o original.</span>
      </label>

      @if (erro(); as e) {
        <p role="alert" class="rounded-lg bg-rose-50 p-3 text-sm text-rose-900">{{ e }}</p>
      }

      <div class="flex gap-2">
        <button type="submit" [disabled]="enviando()"
          class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-bold text-white disabled:opacity-50">
          {{ enviando() ? 'Processando…' : documentoId ? 'Adicionar versão' : 'Cadastrar e processar' }}
        </button>
        <button type="button" (click)="cancelado.emit()" class="rounded-lg px-4 py-2 text-sm font-semibold text-slate-600">Cancelar</button>
      </div>
    </form>
  `,
})
export class KnowledgeDocumentFormComponent {
  private readonly api = inject(KnowledgeApiService);

  /** Com documentoId, o formulario cria uma nova versao do documento existente. */
  @Input() documentoId: string | null = null;
  @Output() salvo = new EventEmitter<Documento>();
  @Output() cancelado = new EventEmitter<void>();

  readonly categorias = CATEGORIAS;
  readonly origem = signal<'texto' | 'arquivo'>('texto');
  readonly arquivo = signal<File | null>(null);
  readonly enviando = signal(false);
  readonly erro = signal<string | null>(null);

  titulo = '';
  categoria: CategoriaDocumento = 'POLITICA';
  responsavel = '';
  fonte = '';
  rotuloVersao = '';
  vigenciaInicio = new Date().toISOString().slice(0, 10);
  vigenciaFim = '';
  texto = '';
  confirma = false;

  ajudaCategoria(): string {
    return CATEGORIAS.find(c => c.valor === this.categoria)?.ajuda ?? '';
  }

  escolher(evento: Event): void {
    const arquivo = (evento.target as HTMLInputElement).files?.[0] ?? null;
    this.erro.set(null);
    if (arquivo && arquivo.size > LIMITE_BYTES) {
      this.erro.set('O arquivo passa de 10 MB. Divida o documento ou cole o texto.');
      this.arquivo.set(null);
      return;
    }
    if (arquivo && !EXTENSOES.some(ext => arquivo.name.toLowerCase().endsWith(ext))) {
      this.erro.set('Envie .pdf, .txt ou .md. Word e imagens não são aceitos.');
      this.arquivo.set(null);
      return;
    }
    this.arquivo.set(arquivo);
  }

  enviar(): void {
    this.erro.set(null);
    const problema = this.validar();
    if (problema) {
      this.erro.set(problema);
      return;
    }
    const vigencia = {
      rotuloVersao: this.rotuloVersao.trim() || null,
      vigenciaInicio: this.vigenciaInicio || null,
      vigenciaFim: this.vigenciaFim || null,
      confirmaSemDadosSensiveis: this.confirma,
    };
    const meta = {
      ...vigencia,
      titulo: this.titulo.trim(),
      categoria: this.categoria,
      responsavel: this.responsavel.trim(),
      fonte: this.fonte.trim() || null,
    };
    const arquivo = this.arquivo();
    const pedido = this.documentoId
      ? this.origem() === 'arquivo' && arquivo
        ? this.api.novaVersaoArquivo(this.documentoId, vigencia, arquivo)
        : this.api.novaVersaoTexto(this.documentoId, { ...vigencia, texto: this.texto })
      : this.origem() === 'arquivo' && arquivo
        ? this.api.cadastrarArquivo(meta, arquivo)
        : this.api.cadastrarTexto({ ...meta, texto: this.texto });
    this.enviando.set(true);
    pedido.subscribe({
      next: doc => {
        this.enviando.set(false);
        this.salvo.emit(doc);
      },
      error: err => {
        this.enviando.set(false);
        const e = erroDaApi(err);
        this.erro.set(e.codigo === 'DUPLICADO' ? 'Já existe uma versão com exatamente este conteúdo.' : e.mensagem);
      },
    });
  }

  private validar(): string | null {
    if (!this.documentoId && (this.titulo.trim().length < 3 || this.responsavel.trim().length < 2)) {
      return 'Preencha título e responsável.';
    }
    if (this.origem() === 'texto' && !this.texto.trim()) return 'Cole o conteúdo do documento.';
    if (this.origem() === 'arquivo' && !this.arquivo()) return 'Escolha um arquivo.';
    if (this.vigenciaFim && this.vigenciaInicio && this.vigenciaFim <= this.vigenciaInicio) {
      return 'O fim da vigência precisa ser depois do início.';
    }
    if (!this.confirma) return 'Confirme que o documento não contém dados pessoais sensíveis.';
    return null;
  }
}
