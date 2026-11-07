import { Injectable } from '@angular/core';
@Injectable({ providedIn: 'root' })
export class SessionService {
  // O adaptador Supabase da tela de login fornece a sessao. Nunca persistir tokens em logs.
  private accessToken: string | null = null;
  private companyId: string | null = null;
  setSession(token: string, empresaId: string): void {
    this.accessToken = token; this.companyId = empresaId;
  }
  clear(): void { this.accessToken = null; this.companyId = null; }
  headers(): Record<string, string> {
    return this.accessToken && this.companyId
      ? { Authorization: `Bearer ${this.accessToken}`, 'X-Empresa-Id': this.companyId } : {};
  }
}
