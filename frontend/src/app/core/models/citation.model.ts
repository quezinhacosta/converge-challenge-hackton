export interface Citacao {
  ref: string; documentoId: string; versaoId: string; trechoId: string;
  titulo: string; versaoRotulo: string; pagina?: number | null;
  secao?: string | null; trecho: string;
}
