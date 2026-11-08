import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RiskCard, ResolveRiskCardPayload } from '../../../../core/models/risk-card.model';
@Component({selector:'app-risk-focus-card',standalone:true,imports:[CommonModule,FormsModule],
 template:`<article *ngIf="card" class="panel risk">
 <header class="risk-header" [class.amber]="card.riskLevel==='AMARELO'">
  <div><span class="pill" [class.rose]="card.riskLevel==='VERMELHO'" [class.amber]="card.riskLevel==='AMARELO'" [class.green]="card.riskLevel==='VERDE'">{{card.riskLevel==='VERMELHO'?'Atenção alta':card.riskLevel==='AMARELO'?'Atenção moderada':'Sem alerta identificado'}}</span>
   <h3>{{card.areaName}}</h3><p class="subtle">{{card.areaHeadcount}} colaboradores · {{card.createdAt | date:'dd/MM/yyyy'}}</p></div>
  <span class="pill gray">Triagem operacional</span>
 </header>
 <div class="risk-body">
  <div><h3>Fator em avaliação</h3><p>{{factor(card.fatorRiscoProvavel)}}</p><p class="subtle">As evidências orientam a revisão do RH. Não representam diagnóstico individual.</p></div>
  <div><h3>Evidências quantitativas</h3><p>{{card.oQueMudouUltimosMeses}}</p></div>
  <div class="context"><h3>Hipótese contextual</h3><p>{{card.contextoOrganizacional}}</p><p class="subtle">Correlação a ser validada pelo RH / SESMT.</p></div>
  <div class="plan"><h3>Plano de ação sugerido</h3><p>{{card.acaoSugerida}}</p>
    <p class="subtle" style="margin-top:8px">Fontes: {{card.fontesConsultadas.join(', ')}}</p>
    <p class="subtle" *ngIf="card.fontesDocumentais?.length">Documentos: <span *ngFor="let c of card.fontesDocumentais">{{c.titulo}} · {{c.versaoRotulo}} </span></p>
  </div>
  <div class="decide" *ngIf="!mode">
   <button class="btn approve" [disabled]="busy" (click)="mode='APROVAR_PGR'">Aprovar e registrar no PGR</button>
   <button class="btn outline" [disabled]="busy" (click)="mode='AJUSTAR_ACAO'; adjusted=card.acaoSugerida">Ajustar medida ou prazo</button>
   <button class="btn danger" [disabled]="busy" (click)="mode='DESCARTAR'">Descartar alerta</button>
  </div>
  <form *ngIf="mode" (ngSubmit)="submit()" class="review" aria-label="Revisar decisão do RH">
   <h3>{{mode==='DESCARTAR'?'Justificar descarte':'Revisar plano de ação'}}</h3>
   <ng-container *ngIf="mode!=='DESCARTAR'"><label for="pgr-deadline">Prazo de acompanhamento (dias)</label><input id="pgr-deadline" type="number" min="15" max="180" [(ngModel)]="days" name="days" required></ng-container>
   <ng-container *ngIf="mode==='AJUSTAR_ACAO'"><label for="pgr-adjust">Medida ajustada</label><textarea id="pgr-adjust" [(ngModel)]="adjusted" name="adjusted" required></textarea></ng-container>
   <ng-container *ngIf="mode==='DESCARTAR'"><label for="pgr-reason">Justificativa</label><textarea id="pgr-reason" [(ngModel)]="reason" name="reason" minlength="5" required></textarea></ng-container>
   <p class="subtle">A decisão será atribuída à sua conta autenticada. A inclusão no PGR não envia comunicações externas.</p>
   <div class="decide"><button class="btn purple" type="submit" [disabled]="busy">{{busy?'Registrando…':'Confirmar decisão'}}</button><button class="btn outline" type="button" [disabled]="busy" (click)="mode=null">Voltar</button></div>
  </form>
 </div></article>`})
export class RiskFocusCardComponent {
 @Input() card!: RiskCard;
 @Input() busy=false;
 @Output() resolve=new EventEmitter<{cardId:string;payload:ResolveRiskCardPayload}>();
 mode:ResolveRiskCardPayload['actionType']|null=null; days=60; adjusted=''; reason='';
 factor(value:string):string { return ({SOBRECARGA_METAS:'Sobrecarga de trabalho e metas',JORNADAS_LONGAS:'Jornadas prolongadas',LIDERANCA_CONFLITO:'Relações de trabalho e apoio da liderança',ASSEDIO:'Encaminhamento para compliance',FALTA_CLAREZA_PAPEL:'Clareza de responsabilidades',FALTA_AUTONOMIA:'Autonomia no trabalho',INSEGURANCA_TRABALHO:'Insegurança no trabalho',ESTAVEL_SEM_FATOR:'Sem fator identificado'} as Record<string,string>)[value]||'Em avaliação'; }
 submit():void {
  if (!this.mode||this.busy) return;
  if (this.mode==='DESCARTAR'&&this.reason.trim().length<5) return;
  if (this.mode!=='DESCARTAR'&&(this.days<15||this.days>180)) return;
  if (this.mode==='AJUSTAR_ACAO'&&!this.adjusted.trim()) return;
  this.resolve.emit({cardId:this.card.cardId,payload:{actionType:this.mode,reviewerName:'RH',deadlineDays:this.mode==='DESCARTAR'?0:this.days,adjustedActionText:this.mode==='AJUSTAR_ACAO'?this.adjusted:undefined,justificationNotes:this.reason||undefined}});
 }
}
