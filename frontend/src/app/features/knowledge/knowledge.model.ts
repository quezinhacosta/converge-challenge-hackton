// Contrato de /api/v1/conhecimento (camelCase). Espelha backend/app/knowledge/dtos.py.

export type CategoriaDocumento =
  | 'POLITICA'
  | 'PROCEDIMENTO_ACOLHIMENTO'
  | 'CANAL_APOIO'
  | 'PROGRAMA_BENEFICIO'
  | 'PLANO_ACAO_ANTERIOR'
  | 'CONTEXTO_ORGANIZACIONAL'
  | 'REFERENCIA_APROVADA';

export type StatusVersao = 'RECEBIDO' | 'PROCESSANDO' | 'PRONTO' | 'ERRO' | 'BLOQUEADO' | 'SUBSTITUIDA';

export const CATEGORIAS: { valor: CategoriaDocumento; rotulo: string; ajuda: string }[] = [
  { valor: 'POLITICA', rotulo: 'Política', ajuda: 'Regras internas aprovadas (ex.: saúde emocional, assédio).' },
  { valor: 'PROCEDIMENTO_ACOLHIMENTO', rotulo: 'Procedimento de acolhimento', ajuda: 'Passo a passo de acolhimento, retorno, revisão de metas.' },
  { valor: 'CANAL_APOIO', rotulo: 'Canal de apoio', ajuda: 'Atendimento psicológico, ouvidoria, canal anônimo.' },
  { valor: 'PROGRAMA_BENEFICIO', rotulo: 'Programa ou benefício', ajuda: 'Programas disponíveis que o agente pode sugerir.' },
  { valor: 'PLANO_ACAO_ANTERIOR', rotulo: 'Plano de ação anterior', ajuda: 'O que já foi tentado e o resultado.' },
  { valor: 'CONTEXTO_ORGANIZACIONAL', rotulo: 'Contexto organizacional', ajuda: 'Mudanças, reestruturações, metas do período.' },
  { valor: 'REFERENCIA_APROVADA', rotulo: 'Referência aprovada', ajuda: 'Guias internos validados pelo jurídico/SST.' },
];

export const ROTULO_CATEGORIA: Record<CategoriaDocumento, string> = Object.fromEntries(
  CATEGORIAS.map(c => [c.valor, c.rotulo]),
) as Record<CategoriaDocumento, string>;

export const ROTULO_STATUS: Record<StatusVersao, string> = {
  RECEBIDO: 'Recebido',
  PROCESSANDO: 'Processando',
  PRONTO: 'Pronto',
  ERRO: 'Erro',
  BLOQUEADO: 'Bloqueado (dado sensível)',
  SUBSTITUIDA: 'Substituída',
};

export interface Versao {
  id: string;
  numero: number;
  rotulo: string;
  origem: 'TEXTO' | 'UPLOAD';
  status: StatusVersao;
  publicada: boolean;
  vigenciaInicio: string;
  vigenciaFim: string | null;
  tamanhoBytes: number;
  nomeArquivo: string | null;
  erroCodigo: string | null;
  erroMensagem: string | null;
  achadosSensiveis: string[];
  tentativas: number;
  criadoEm: string;
  processadoEm: string | null;
  publicadaEm: string | null;
  quantidadeTrechos: number;
}

export interface Documento {
  id: string;
  titulo: string;
  categoria: CategoriaDocumento;
  responsavel: string;
  fonte: string | null;
  escopoAcesso: string;
  criadoEm: string;
  atualizadoEm: string;
  versaoPublicada: Versao | null;
  versoes: Versao[];
}

export interface MetadadosDocumento {
  titulo: string;
  categoria: CategoriaDocumento;
  responsavel: string;
  fonte?: string | null;
  rotuloVersao?: string | null;
  vigenciaInicio?: string | null;
  vigenciaFim?: string | null;
  confirmaSemDadosSensiveis: boolean;
}

export interface CadastroTexto extends MetadadosDocumento {
  texto: string;
}

export interface TrechoRecuperado {
  ref: string;
  trechoId: string;
  documentoId: string;
  versaoId: string;
  titulo: string;
  categoria: CategoriaDocumento;
  versaoNumero: number;
  versaoRotulo: string;
  vigenciaInicio: string;
  vigenciaFim: string | null;
  pagina: number | null;
  secao: string | null;
  texto: string;
  score: number;
  suspeitoInjecao: boolean;
}

export interface ResultadoRecuperacao {
  trechos: TrechoRecuperado[];
  evidenciaSuficiente: boolean;
  motivoInsuficiencia: string | null;
  possivelConflito: string[][];
  metodo: string;
  latenciaMs: number;
}

export interface Pendencia {
  tipo:
    | 'VENCENDO'
    | 'VENCIDO_PUBLICADO'
    | 'PRONTO_SEM_PUBLICAR'
    | 'ERRO_PROCESSAMENTO'
    | 'BLOQUEADO_SENSIVEL'
    | 'LACUNA_FATOR'
    | 'SEM_CANAL_DE_APOIO';
  mensagem: string;
  responsavel: string | null;
  documentoId: string | null;
  versaoId: string | null;
  prazo: string | null;
  fator: string | null;
}

export interface StatusBase {
  disponivel: boolean;
  documentos: number;
  publicados: number;
  comErroOuBloqueio: number;
}

/** Erro padronizado do backend: { detail: { codigo, mensagem, detalhes } }. */
export interface ErroApi {
  codigo: string;
  mensagem: string;
  detalhes?: Record<string, unknown>;
}

export function erroDaApi(err: unknown): ErroApi {
  const e = err as { status?: number; error?: { detail?: unknown } };
  const detail = e?.error?.detail;
  if (detail && typeof detail === 'object' && 'mensagem' in detail) return detail as ErroApi;
  if (e?.status === 0) return { codigo: 'SEM_CONEXAO', mensagem: 'Não foi possível falar com o servidor.' };
  if (e?.status === 401) return { codigo: 'NAO_AUTENTICADO', mensagem: 'Sua sessão expirou. Entre novamente.' };
  if (e?.status === 503) return { codigo: 'NAO_CONFIGURADO', mensagem: 'Base de conhecimento indisponível neste ambiente.' };
  return { codigo: 'ERRO', mensagem: 'Algo deu errado. Tente de novo.' };
}
