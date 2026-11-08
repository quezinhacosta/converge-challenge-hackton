import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  CadastroTexto,
  CategoriaDocumento,
  Documento,
  MetadadosDocumento,
  Pendencia,
  ResultadoRecuperacao,
  StatusBase,
  Versao,
} from './knowledge.model';

/** Cliente de /api/v1/conhecimento. O token e a empresa vem do authInterceptor (nunca do body). */
@Injectable({ providedIn: 'root' })
export class KnowledgeApiService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/conhecimento`;

  status(): Observable<StatusBase> {
    return this.http.get<StatusBase>(`${this.base}/status`);
  }

  listar(categoria?: CategoriaDocumento): Observable<Documento[]> {
    const params = categoria ? new HttpParams().set('categoria', categoria) : undefined;
    return this.http.get<Documento[]>(`${this.base}/documentos`, { params });
  }

  obter(id: string): Observable<Documento> {
    return this.http.get<Documento>(`${this.base}/documentos/${encodeURIComponent(id)}`);
  }

  cadastrarTexto(payload: CadastroTexto): Observable<Documento> {
    return this.http.post<Documento>(`${this.base}/documentos`, payload);
  }

  cadastrarArquivo(meta: MetadadosDocumento, arquivo: File): Observable<Documento> {
    return this.http.post<Documento>(`${this.base}/documentos/arquivo`, this.formulario(meta, arquivo));
  }

  novaVersaoTexto(id: string, payload: Omit<CadastroTexto, 'titulo' | 'categoria' | 'responsavel' | 'fonte'>): Observable<Documento> {
    return this.http.post<Documento>(`${this.base}/documentos/${encodeURIComponent(id)}/versoes`, payload);
  }

  novaVersaoArquivo(
    id: string,
    meta: Pick<MetadadosDocumento, 'rotuloVersao' | 'vigenciaInicio' | 'vigenciaFim' | 'confirmaSemDadosSensiveis'>,
    arquivo: File,
  ): Observable<Documento> {
    return this.http.post<Documento>(
      `${this.base}/documentos/${encodeURIComponent(id)}/versoes/arquivo`,
      this.formulario(meta, arquivo),
    );
  }

  atualizarMetadados(id: string, campos: Partial<Pick<Documento, 'titulo' | 'categoria' | 'responsavel' | 'fonte'>>): Observable<Documento> {
    return this.http.patch<Documento>(`${this.base}/documentos/${encodeURIComponent(id)}`, campos);
  }

  publicar(versaoId: string): Observable<Documento> {
    return this.http.post<Documento>(`${this.base}/versoes/${encodeURIComponent(versaoId)}/publicar`, {});
  }

  despublicar(versaoId: string): Observable<Documento> {
    return this.http.post<Documento>(`${this.base}/versoes/${encodeURIComponent(versaoId)}/despublicar`, {});
  }

  reprocessar(versaoId: string): Observable<Versao> {
    return this.http.post<Versao>(`${this.base}/versoes/${encodeURIComponent(versaoId)}/reprocessar`, {});
  }

  excluir(id: string): Observable<void> {
    return this.http.delete<void>(`${this.base}/documentos/${encodeURIComponent(id)}`);
  }

  buscar(texto: string, fatorNr1?: string | null): Observable<ResultadoRecuperacao> {
    return this.http.post<ResultadoRecuperacao>(`${this.base}/buscar`, { texto, fatorNr1: fatorNr1 || null });
  }

  pendencias(): Observable<{ geradoEm: string; pendencias: Pendencia[] }> {
    return this.http.get<{ geradoEm: string; pendencias: Pendencia[] }>(`${this.base}/pendencias`);
  }

  private formulario(campos: Partial<MetadadosDocumento>, arquivo: File): FormData {
    const form = new FormData();
    form.append('arquivo', arquivo, arquivo.name);
    for (const [chave, valor] of Object.entries(campos)) {
      if (valor === null || valor === undefined || valor === '') continue;
      form.append(chave, String(valor));
    }
    return form;
  }
}
