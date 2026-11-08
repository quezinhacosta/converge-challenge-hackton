import { Component, EventEmitter, OnInit, Output, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { KnowledgeApiService } from '../knowledge-api.service';
import { Pendencia, erroDaApi } from '../knowledge.model';

const ROTULO: Record<Pendencia['tipo'], { titulo: string; cor: string }> = {
  VENCIDO_PUBLICADO: { titulo: 'Vigência vencida', cor: 'bg-rose-100 text-rose-800' },
  BLOQUEADO_SENSIVEL: { titulo: 'Bloqueado por dado sensível', cor: 'bg-amber-100 text-amber-900' },
  ERRO_PROCESSAMENTO: { titulo: 'Erro de processamento', cor: 'bg-rose-100 text-rose-800' },
  VENCENDO: { titulo: 'Vence em breve', cor: 'bg-amber-100 text-amber-900' },
  PRONTO_SEM_PUBLICAR: { titulo: 'Pronto e não publicado', cor: 'bg-sky-100 text-sky-800' },
  SEM_CANAL_DE_APOIO: { titulo: 'Sem canal de apoio', cor: 'bg-rose-100 text-rose-800' },
  LACUNA_FATOR: { titulo: 'Lacuna por fator de risco', cor: 'bg-slate-100 text-slate-700' },
};

/** Tarefas de cuidado da base que o digital worker gera (com responsavel e prazo). */
@Component({
  selector: 'app-knowledge-pending-list',
  standalone: true,
  imports: [DatePipe],
  template: `
    @if (erro(); as e) { <p role="alert" class="rounded-lg bg-rose-50 p-3 text-sm text-rose-900">{{ e }}</p> }
    @if (carregando()) { <p class="text-sm text-slate-500">Revisando a base…</p> }
    @if (!carregando() && !erro() && !pendencias().length) {
      <p class="rounded-lg bg-emerald-50 p-3 text-sm text-emerald-900">Nenhuma pendência. A base está em dia.</p>
    }
    <ul class="space-y-2">
      @for (p of pendencias(); track $index) {
        <li class="rounded-lg border border-slate-200 p-3 text-sm">
          <div class="flex flex-wrap items-center gap-2">
            <span class="rounded px-2 py-0.5 text-xs font-bold" [class]="rotulo[p.tipo].cor">{{ rotulo[p.tipo].titulo }}</span>
            @if (p.prazo) { <span class="text-xs text-slate-500">prazo {{ p.prazo | date: 'dd/MM/yyyy' }}</span> }
            @if (p.responsavel) { <span class="text-xs text-slate-500">· {{ p.responsavel }}</span> }
            @if (p.documentoId) {
              <button class="ml-auto text-xs font-semibold text-indigo-700" (click)="abrir.emit(p.documentoId)">Abrir documento</button>
            }
          </div>
          <p class="mt-1 text-slate-700">{{ p.mensagem }}</p>
        </li>
      }
    </ul>
  `,
})
export class KnowledgePendingListComponent implements OnInit {
  private readonly api = inject(KnowledgeApiService);
  @Output() abrir = new EventEmitter<string>();
  readonly rotulo = ROTULO;
  readonly pendencias = signal<Pendencia[]>([]);
  readonly carregando = signal(true);
  readonly erro = signal<string | null>(null);

  ngOnInit(): void {
    this.recarregar();
  }

  recarregar(): void {
    this.carregando.set(true);
    this.api.pendencias().subscribe({
      next: r => {
        this.carregando.set(false);
        this.pendencias.set(r.pendencias);
      },
      error: err => {
        this.carregando.set(false);
        this.erro.set(erroDaApi(err).mensagem);
      },
    });
  }
}
