import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { PgrInventoryItem } from '../../../../core/models/nr1.model';
@Component({selector:'app-pgr-inventory-table',standalone:true,imports:[CommonModule,RouterLink],
 template:`<section class="panel inventory" aria-labelledby="inventory-title">
 <header class="inventory-head"><div><p class="eyebrow">GRO / PGR</p><h2 id="inventory-title">Inventário de riscos e medidas</h2><p class="subtle">Decisões registradas pelo RH e seus prazos de acompanhamento.</p></div><a class="btn outline" routerLink="/acoes-rh">Acompanhar ações</a></header>
 <div class="table-wrap" tabindex="0" role="region" aria-label="Inventário PGR"><table><thead><tr><th>Código</th><th>Setor</th><th>Medida</th><th>Responsável</th><th>Prazo</th><th>Status</th></tr></thead><tbody>
 <tr *ngFor="let item of items"><td>{{item.itemId}}</td><td>{{item.areaName}}</td><td>{{item.actionPlanDescription}}</td><td>{{item.responsiblePerson}}</td><td>{{item.deadlineDate | date:'dd/MM/yyyy'}}</td><td><span class="pill" [class.green]="!!item.closureDate" [class.violet]="!item.closureDate">{{item.closureDate?'Encerrado':'Em acompanhamento'}}</span></td></tr>
 <tr *ngIf="!items.length"><td colspan="6" class="empty-state">Nenhuma medida registrada nesta consulta.</td></tr></tbody></table></div>
 <details class="audit"><summary>Histórico de decisões</summary><ul><ng-container *ngFor="let item of items"><li *ngFor="let entry of item.auditLog">{{entry}}</li></ng-container></ul><p class="subtle" *ngIf="!items.length">O histórico será exibido após uma decisão registrada.</p></details>
 </section>`})
export class PgrInventoryTableComponent {
 @Input() items:PgrInventoryItem[]=[];
 @Output() reassess=new EventEmitter<string>();
}
