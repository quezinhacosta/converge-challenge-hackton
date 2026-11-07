/**
 * Servico Angular para integracao com a API FastAPI do Pulso.
 */

import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AreaInfo, PgrInventoryItem } from '../models/nr1.model';
import { AreaHistoryComparison } from '../models/signals.model';
import { ResolveRiskCardPayload, RiskCard } from '../models/risk-card.model';

@Injectable({
  providedIn: 'root',
})
export class PulsoApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = 'http://localhost:8000/api/v1';

  listAreas(): Observable<AreaInfo[]> {
    return this.http.get<AreaInfo[]>(`${this.baseUrl}/areas`);
  }

  getAreaSignals(areaId: string): Observable<AreaHistoryComparison> {
    return this.http.get<AreaHistoryComparison>(`${this.baseUrl}/areas/${areaId}/signals`);
  }

  listActiveRiskCards(): Observable<RiskCard[]> {
    return this.http.get<RiskCard[]>(`${this.baseUrl}/risk-cards/active`);
  }

  resolveRiskCard(cardId: string, payload: ResolveRiskCardPayload): Observable<PgrInventoryItem> {
    return this.http.post<PgrInventoryItem>(`${this.baseUrl}/risk-cards/${cardId}/resolve`, payload);
  }

  getPgrInventory(): Observable<PgrInventoryItem[]> {
    return this.http.get<PgrInventoryItem[]>(`${this.baseUrl}/pgr/inventory`);
  }

  sendChatQuery(queryText: string): Observable<{
    replyText: string;
    isRefusal: boolean;
    refusalReason?: string;
    sourcesUsed: string[];
  }> {
    return this.http.post<{
      replyText: string;
      isRefusal: boolean;
      refusalReason?: string;
      sourcesUsed: string[];
    }>(`${this.baseUrl}/chat`, {
      user_id: 'rh_user_01',
      user_name: 'Analista de RH',
      query_text: queryText,
    });
  }
}
