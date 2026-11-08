import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { KnowledgeApiService } from '../knowledge-api.service';
import { ROTULO_CATEGORIA, ResultadoRecuperacao, erroDaApi } from '../knowledge.model';

const FATORES = [
  { valor: '', rotulo: 'Sem fator' },
  { valor: 'SOBRECARGA_METAS', rotulo: 'Sobrecarga e metas' },
  { valor: 'JORNADAS_LONGAS', rotulo: 'Jornadas longas' },
  { valor: 'LIDERANCA_CONFLITO', rotulo: 'Conflito com liderança' },
  { valor: 'ASSEDIO', rotulo: 'Assédio' },
  { valor: 'FALTA_CLAREZA_PAPEL', rotulo: 'Falta de clareza de papel' },
  { valor: 'FALTA_AUTONOMIA', rotulo: 'Falta de autonomia' },
  { valor: 'INSEGURANCA_TRABALHO', rotulo: 'Insegurança no trabalho' },
];

/** Pre-visualizacao: mostra ao RH exatamente o que o agente recuperaria (sem gerar resposta). */
@Component({
  selector: 'app-knowledge-search-test',
  standalone: true,
  imports: [FormsModule],
  template: `
    <form class="flex flex-wrap gap-2" (ngSubmit)="buscar()">
      <input name="q" [(ngModel)]="texto" minlength="3" maxlength="500" required
        class="min-w-[16rem] flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm"
        placeholder="Ex.: que apoio psicológico a empresa oferece?" aria-label="Pergunta de teste" />
      <select name="fator" [(ngModel)]="fator" class="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm" aria-label="Fator de risco">
        @for (f of fatores; track f.valor) { <option [value]="f.valor">{{ f.rotulo }}</option> }
      </select>
      <button class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-bold text-white disabled:opacity-50"
        [disabled]="carregando() || texto.trim().length < 3">{{ carregando() ? 'Buscando…' : 'Testar busca' }}</button>
    </form>
    <p class="mt-2 text-xs text-slate-500">Só aparecem versões publicadas e vigentes desta empresa. Nenhuma resposta é gerada aqui.</p>

    @if (erro(); as e) { <p role="alert" class="mt-4 rounded-lg bg-rose-50 p-3 text-sm text-rose-900">{{ e }}</p> }

    @if (resultado(); as r) {
      <div class="mt-4 space-y-3">
        @if (!r.evidenciaSuficiente) {
          <p class="rounded-lg bg-amber-50 p-3 text-sm text-amber-950">
            <strong>Sem evidência suficiente.</strong> {{ r.motivoInsuficiencia }}
            O agente responderá que não encontrou base documental. Considere cadastrar um documento sobre o tema.
          </p>
        }
        @if (r.possivelConflito.length) {
          <p class="rounded-lg bg-sky-50 p-3 text-sm text-sky-900">Documentos diferentes da mesma categoria apareceram juntos ({{ conflitos(r) }}). Confira se não se contradizem.</p>
        }
        @for (t of r.trechos; track t.trechoId) {
          <article class="rounded-lg border border-slate-200 p-3">
            <header class="flex flex-wrap items-center gap-2 text-xs">
              <span class="rounded bg-indigo-600 px-1.5 py-0.5 font-bold text-white">{{ t.ref }}</span>
              <span class="font-semibold text-slate-900">{{ t.titulo }}</span>
              <span class="text-slate-500">{{ rotuloCategoria[t.categoria] }} · versão {{ t.versaoRotulo }}
                @if (t.pagina) { · pág. {{ t.pagina }} } @if (t.secao) { · {{ t.secao }} }</span>
              @if (t.suspeitoInjecao) {
                <span class="rounded bg-amber-100 px-1.5 py-0.5 font-bold text-amber-900"
                  title="Texto parecido com instrução ao agente. É tratado só como dado.">Parece instrução</span>
              }
              <span class="ml-auto text-slate-400">relevância {{ t.score.toFixed(2) }}</span>
            </header>
            <p class="mt-2 whitespace-pre-line text-sm text-slate-700">{{ t.texto }}</p>
          </article>
        }
        <p class="text-xs text-slate-400">{{ r.metodo }} · {{ r.latenciaMs }} ms</p>
      </div>
    }
  `,
})
export class KnowledgeSearchTestComponent {
  private readonly api = inject(KnowledgeApiService);
  readonly fatores = FATORES;
  readonly rotuloCategoria = ROTULO_CATEGORIA;
  readonly carregando = signal(false);
  readonly erro = signal<string | null>(null);
  readonly resultado = signal<ResultadoRecuperacao | null>(null);
  texto = '';
  fator = '';

  conflitos(r: ResultadoRecuperacao): string {
    return r.possivelConflito.map(par => par.join(' e ')).join('; ');
  }

  buscar(): void {
    if (this.texto.trim().length < 3) return;
    this.carregando.set(true);
    this.erro.set(null);
    this.api.buscar(this.texto.trim(), this.fator).subscribe({
      next: r => {
        this.carregando.set(false);
        this.resultado.set(r);
      },
      error: err => {
        this.carregando.set(false);
        this.erro.set(erroDaApi(err).mensagem);
      },
    });
  }
}
