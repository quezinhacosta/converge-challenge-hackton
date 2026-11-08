import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { PulsoApiService } from './core/services/pulso-api.service';
import { RiskCard, ResolveRiskCardPayload } from './core/models/risk-card.model';
import { AreaInfo, PgrInventoryItem } from './core/models/nr1.model';
import { AreaHistoryComparison } from './core/models/signals.model';
import { RiskFocusCardComponent } from './features/rh-dashboard/components/risk-focus-card/risk-focus-card.component';
import { PgrInventoryTableComponent } from './features/rh-dashboard/components/pgr-inventory-table/pgr-inventory-table.component';
import { AgentChatConsoleComponent } from './features/rh-dashboard/components/agent-chat-console/agent-chat-console.component';
@Component({selector:'app-dashboard',standalone:true,imports:[CommonModule,RouterLink,RiskFocusCardComponent,PgrInventoryTableComponent,AgentChatConsoleComponent],
 template:`<div class="top"><div>Governança ocupacional / <strong>Visão executiva</strong></div><span class="demo">{{demo()?'Dados de demonstração':'Dados da empresa autenticada'}}</span></div>
 <section id="visao"><header class="hero"><svg class="hero-art" viewBox="0 0 410 340" aria-hidden="true"><path fill="#7d39eb" d="M55 10h125q38 0 38 38v60q0 32 32 32h122q38 0 38 38v124q0 38-38 38H55q-38 0-38-38V48q0-38 38-38Z"/><rect x="255" y="35" width="70" height="70" rx="15" fill="#c6ff33"/></svg>
  <p class="eyebrow">VYTAL.ai · Digital Worker</p><h1>Governança de riscos psicossociais</h1><p>Evidências, decisões e acompanhamento das ações do RH.</p>
  <div class="hero-bottom"><div class="hero-status"><span class="pill green">Decisão humana</span><span class="pill">{{loading()?'Atualizando informações':'Ciclo de acompanhamento'}}</span></div><button class="btn lime" (click)="closeCycle()" [disabled]="closing()||loading()">{{closing()?'Analisando áreas…':'Executar fechamento'}}</button></div>
 </header>
 <div *ngIf="message()" class="notice" [class.error]="error()" role="status">{{message()}}</div>
 <div class="kpis" aria-label="Indicadores consolidados"><div class="kpi"><div class="kpi-head">Colaboradores cadastrados</div><span class="num">{{loaded()?people():'—'}}</span><p class="subtle">{{areas.length}} áreas nesta consulta</p></div>
 <div class="kpi"><div class="kpi-head">Focos pendentes</div><span class="num">{{loaded()?cards.length:'—'}}</span><p class="subtle">Aguardando deliberação do RH</p></div>
 <div class="kpi"><div class="kpi-head">Medidas no PGR</div><span class="num">{{loaded()?inventory.length:'—'}}</span><p class="subtle">{{openPgr()}} em acompanhamento</p></div>
 <div class="kpi"><div class="kpi-head">Acompanhamento operacional</div><a class="btn purple" routerLink="/acoes-rh">Ações do RH ↗</a><p class="subtle">Tarefas, prazos e evidências</p></div></div></section>
 <div class="split"><section id="deliberacao"><header class="section-title"><div><h2>Fila de deliberação</h2><p class="subtle">Analise as evidências e revise a medida sugerida.</p></div><span class="pill violet">Revisão humana</span></header>
 <app-risk-focus-card *ngIf="focusCard() as card" [card]="card" [busy]="resolving()===card.cardId" (resolve)="resolveCard($event)" />
 <article *ngIf="!focusCard()" class="panel quiet-card"><span class="pill gray">{{selectedArea()?.isAnonymized?'Área protegida':'Acompanhamento'}}</span><h3>{{selectedArea()?.name||'Nenhuma área selecionada'}}</h3>
  <p>{{selectedArea()?.isAnonymized?'Os indicadores desta área ficam ocultos por quórum reduzido.':loaded()?'Nenhum card aberto foi retornado para esta área. Isso não comprova ausência de risco.':'Os dados serão exibidos após autenticação e conexão com a API.'}}</p>
  <p class="subtle" *ngIf="signals() as data">{{data.eventosContextoRecentes.join(' · ')}}</p>
 </article>
 <div class="panel panel-pad block" *ngIf="signals() as data"><h3>Evolução dos indicadores</h3><div class="metrics" style="margin-top:12px"><div class="metric"><dt>Dias de atestado</dt><dd class="num">{{data.variacaoDiasAtestadoPct}}%</dd><dd>Variação histórica</dd></div><div class="metric"><dt>Horas extras</dt><dd class="num">{{data.variacaoHorasExtrasPct}}%</dd><dd>Variação histórica</dd></div><div class="metric"><dt>Pedidos de demissão</dt><dd class="num">{{data.pedidosDemissaoPeriodo}}</dd><dd>No período consultado</dd></div><div class="metric"><dt>Pesquisa de carga</dt><dd class="num">{{data.notaCargaTrabalhoAtual ?? '—'}}</dd><dd>Somente respostas disponíveis</dd></div></div></div>
 </section>
 <section id="setores"><header class="section-title"><div><h2>Matriz de setores</h2><p class="subtle">Selecione uma área para acompanhar.</p></div></header><div class="panel sectors">
  <ng-container *ngFor="let area of areas"><article *ngIf="area.isAnonymized" class="locked"><strong>{{area.name}}</strong><span class="pill gray">Protegido por quórum</span><p class="subtle">Indicadores ocultos.</p></article>
   <button *ngIf="!area.isAnonymized" class="sector" (click)="selectArea(area.id)" [attr.aria-pressed]="selected()===area.id"><span><strong>{{area.name}}</strong><span class="subtle">{{area.headcount}} colaboradores</span></span><span class="pill" [class.rose]="areaTone(area.id)==='rose'" [class.amber]="areaTone(area.id)==='amber'" [class.gray]="areaTone(area.id)==='gray'">{{areaTone(area.id)==='rose'?'Alta':areaTone(area.id)==='amber'?'Moderada':'Em acompanhamento'}}</span></button>
  </ng-container><p class="empty-state" *ngIf="!areas.length">Nenhuma área disponível.</p></div></section></div>
 <section id="inventario" class="block"><app-pgr-inventory-table [items]="inventory" /></section>
 <section class="block"><header class="section-title"><div><h2>Assistente do RH</h2><p class="subtle">Investigue evidências e prepare propostas para revisão.</p></div><a routerLink="/acoes-rh" class="btn outline">Abrir ações preparadas</a></header><app-agent-chat-console /></section>
 <footer>VYTAL.ai · Análise por área, decisão humana e trilha de acompanhamento. Indicadores operacionais não são diagnósticos.</footer>`})
export class DashboardComponent implements OnInit {
 private api=inject(PulsoApiService);
 areas:AreaInfo[]=[];cards:RiskCard[]=[];inventory:PgrInventoryItem[]=[];
 selected=signal('');signals=signal<AreaHistoryComparison|null>(null);demo=signal(false);
 loading=signal(false);loaded=signal(false);closing=signal(false);resolving=signal<string|null>(null);
 message=signal('');error=signal(false);
 ngOnInit():void {this.load();}
 people():number{return this.areas.reduce((sum,a)=>sum+a.headcount,0);}
 openPgr():number{return this.inventory.filter(i=>!i.closureDate).length;}
 selectedArea():AreaInfo|undefined{return this.areas.find(a=>a.id===this.selected());}
 focusCard():RiskCard|undefined{return this.cards.find(c=>c.areaId===this.selected());}
 areaTone(id:string):string {const level=this.cards.find(c=>c.areaId===id)?.riskLevel;return level==='VERMELHO'?'rose':level==='AMARELO'?'amber':'gray';}
 fail(error:{status?:number}):void {this.error.set(true);this.message.set(error.status===401?'Entre com sua conta de RH para consultar os dados.':error.status===403?'Sua conta não tem acesso a esta empresa.':'Não foi possível concluir a consulta. Nenhum sucesso foi registrado.');}
 load():void {
  this.loading.set(true);
  forkJoin({health:this.api.health(),areas:this.api.listAreas(),cards:this.api.listActiveRiskCards(),pgr:this.api.getPgrInventory()}).subscribe({next:r=>{
   this.demo.set(r.health.mode==='demo');this.areas=r.areas;this.cards=r.cards;this.inventory=r.pgr;this.loaded.set(true);this.loading.set(false);
   const id=this.areas.find(a=>a.id===this.selected())?.id||this.cards[0]?.areaId||this.areas.find(a=>!a.isAnonymized)?.id||'';
   if(id)this.selectArea(id);
  },error:e=>{this.loading.set(false);this.loaded.set(false);this.areas=[];this.cards=[];this.inventory=[];this.signals.set(null);this.fail(e);}});
 }
 selectArea(id:string):void {
  this.selected.set(id);this.signals.set(null);
  if(this.areas.find(a=>a.id===id)?.isAnonymized)return;
  this.api.getAreaSignals(id).subscribe({next:data=>{if(this.selected()===id&&!data.isAnonymized)this.signals.set(data);},error:e=>this.fail(e)});
 }
 closeCycle():void {this.closing.set(true);this.api.closeCycle().subscribe({next:()=>{this.closing.set(false);this.error.set(false);this.message.set('Fechamento concluído. Revise os resultados e as pendências.');this.load();},error:e=>{this.closing.set(false);this.fail(e);}});}
 resolveCard(event:{cardId:string;payload:ResolveRiskCardPayload}):void {
  this.resolving.set(event.cardId);this.api.resolveRiskCard(event.cardId,event.payload).subscribe({next:()=>{this.resolving.set(null);this.error.set(false);this.message.set(event.payload.actionType==='DESCARTAR'?'Alerta descartado com justificativa.':'Medida registrada no PGR. O acompanhamento pode ser preparado em Ações do RH.');this.load();},error:e=>{this.resolving.set(null);this.fail(e);}});
 }
}
