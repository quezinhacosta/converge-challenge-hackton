import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { AreaInfo, PgrInventoryItem } from '../models/nr1.model';
import { AreaHistoryComparison } from '../models/signals.model';
import { ResolveRiskCardPayload, RiskCard } from '../models/risk-card.model';

import { Citacao } from '../models/citation.model';
export interface ChatResponse {
  replyText: string; isRefusal: boolean; refusalReason?: string;
  sourcesUsed: string[]; suggestedAction?: string; citacoes?: Citacao[];
}
@Injectable({ providedIn: 'root' })
export class PulsoApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;
  health(): Observable<{status: string; mode: string}> {
    return this.http.get<{status: string; mode: string}>(`${this.baseUrl}/health`);
  }
  listAreas(): Observable<AreaInfo[]> {
    return this.http.get<AreaInfo[]>(`${this.baseUrl}/areas`);
  }
  getAreaSignals(areaId: string): Observable<AreaHistoryComparison> {
    return this.http.get<AreaHistoryComparison>(`${this.baseUrl}/areas/${encodeURIComponent(areaId)}/signals`);
  }
  listActiveRiskCards(): Observable<RiskCard[]> {
    return this.http.get<RiskCard[]>(`${this.baseUrl}/risk-cards/active`);
  }
  resolveRiskCard(cardId: string, payload: ResolveRiskCardPayload): Observable<PgrInventoryItem> {
    return this.http.post<PgrInventoryItem>(`${this.baseUrl}/risk-cards/${encodeURIComponent(cardId)}/resolve`, payload);
  }
  getPgrInventory(): Observable<PgrInventoryItem[]> {
    return this.http.get<PgrInventoryItem[]>(`${this.baseUrl}/pgr/inventory`);
  }
  reassessPgrItem(itemId: string): Observable<{ houveMelhora: boolean; parecer: string; reducaoAtestadosPct: number }> {
    return this.http.post<{ houveMelhora: boolean; parecer: string; reducaoAtestadosPct: number }>(`${this.baseUrl}/pgr/${encodeURIComponent(itemId)}/reassess`, {});
  }
  sendChatQuery(queryText: string): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(`${this.baseUrl}/chat`, {
      user_id: 'authenticated', user_name: 'RH', query_text: queryText,
    });
  }
}
