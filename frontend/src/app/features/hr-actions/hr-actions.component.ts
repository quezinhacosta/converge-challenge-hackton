import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { forkJoin, Observable } from 'rxjs';
import { PulsoApiService } from '../../core/services/pulso-api.service';
import { AreaInfo } from '../../core/models/nr1.model';
import { HrActionsApi, RhAction, RhTask, Intervention, Readiness, Pending, History, WorkerCycle } from './hr-actions-api.service';
@Component({selector:'app-hr-actions',standalone:true,imports:[CommonModule,FormsModule],templateUrl:'./hr-actions.component.html'})
export class HrActionsComponent implements OnInit {
 private api=inject(HrActionsApi); private pulso=inject(PulsoApiService);
 cycle:WorkerCycle|null=null;
 areas:AreaInfo[]=[];interventions:Intervention[]=[];pending:Pending={actions:[],tasks:[],asOf:''};
 readiness:Readiness={externalEnabled:false,slackConfigured:false,calendarConfigured:false,slackChannels:[],calendars:[],allowedAttendees:[]};
 selected:Intervention|null=null;history:History|null=null;review:RhAction|null=null;confirmation=false;
 loading=false;busy=false;message='';error=false;connected=false;
 timezone=Intl.DateTimeFormat().resolvedOptions().timeZone;
 areaId='';title='';objective='';due=this.localDate(15);taskTitle='Acompanhar intervenção e reunir evidências';
 reminderChannel='';maxReminders=2;intervalDays=7;
 actionKind:'TASK'|'SLACK'|'CALENDAR'='TASK';channel='';calendar='';
 starts=this.localDate(2);ends=this.localDate(2,1);attendees='';reevaluation=false;
 evidenceTask:RhTask|null=null;evidenceText='';evidenceUrl='';
 uncertain:RhAction|null=null;outcome:'CONFIRMED'|'NOT_DELIVERED'='CONFIRMED';externalRef='';reconciliationNote='';
 private keys=new Map<string,string>();
 private actionDrafts=new Map<string,{payload:unknown;notBefore:string}>();
 runCycle():void {if(this.busy||this.loading||!this.connected)return;this.cycle=null;this.execute(this.api.cycle(),'Ciclo concluído. As propostas aguardam revisão do RH; nenhuma mensagem foi enviada.',result=>this.cycle=result);}
 cycleState(value:string):string{return ({PROPOSTA_PREPARADA:'Proposta preparada',PROPOSTA_JA_EXISTIA:'Proposta já existente',FLUXO_COMPLIANCE:'Encaminhamento ao compliance',BLOQUEADO:'Requer conferência'} as Record<string,string>)[value]||'Resultado para revisão';}
 downloadReport():void {if(this.busy||!this.connected)return;this.busy=true;this.error=false;this.api.report().subscribe({next:blob=>{this.busy=false;const url=URL.createObjectURL(blob);const link=document.createElement('a');link.href=url;link.download=`vytal-ai-relatorio-nr1-${new Date().toISOString().slice(0,10)}.pdf`;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);this.message='Relatório gerado com dados agregados por área.';},error:e=>this.fail(e)});}
 cycleCount(value:string):number{return this.cycle?.cards.filter(c=>c.resultado===value).length||0;}
 slackCount():number{return this.cycle?.cards.filter(c=>c.avisoSlack).length||0;}
 ngOnInit():void {this.load();}
 localDate(days:number,hours=0):string {const date=new Date();date.setDate(date.getDate()+days);date.setHours(10+hours,0,0,0);return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}T${String(date.getHours()).padStart(2,'0')}:00`;}
 key(body:unknown):string {const value=JSON.stringify(body);if(!this.keys.has(value))this.keys.set(value,crypto.randomUUID());return this.keys.get(value)!;}
 label(status:string):string {return ({PENDING:'Aguardando aprovação',QUEUED:'Agendada para execução',RUNNING:'Em execução',SUCCEEDED:'Execução confirmada',BLOCKED:'Requer configuração ou revisão',UNKNOWN:'Conferência necessária',FAILED:'Não concluída',CANCELLED:'Cancelada',OPEN:'Em acompanhamento',DONE:'Concluída'} as Record<string,string>)[status]||'Em acompanhamento';}
 kind(value:string):string {return ({TASK:'Tarefa de acompanhamento',SLACK:'Mensagem ao canal do RH',CALENDAR:'Compromisso na agenda'} as Record<string,string>)[value]||'Ação do RH';}
 eventLabel(value:string):string {return ({INTERVENTION_PREPARED:'Intervenção preparada',ACTION_PREPARED:'Ação preparada para revisão',ACTION_APPROVED:'Ação aprovada pelo RH',ACTION_CANCELLED:'Ação cancelada',EXECUTION_STARTED:'Execução iniciada',EXECUTION_SUCCEEDED:'Execução confirmada',EXECUTION_QUEUED:'Nova tentativa agendada',EXECUTION_BLOCKED:'Execução bloqueada para revisão',EXECUTION_UNKNOWN:'Resultado pendente de conferência',EXECUTION_FAILED:'Execução não concluída',EVIDENCE_RECORDED:'Evidência registrada pelo RH',TASK_COMPLETED_BY_RH:'Tarefa concluída pelo RH',TASK_CANCELLED_BY_RH:'Tarefa cancelada pelo RH',OUTCOME_RECONCILED_BY_RH:'Resultado conferido pelo RH',REMINDER_AUTHORIZED_BY_POLICY:'Lembrete autorizado pela política aprovada',EXECUTION_LEASE_EXPIRED:'Execução interrompida; resultado revisado',RETRY_REQUESTED:'Nova tentativa solicitada',NEW_REVIEW_REQUESTED:'Nova revisão solicitada'} as Record<string,string>)[value]||'Atualização registrada';}
 fail(e:{status?:number;error?:{detail?:{message?:string}}}):void {this.busy=false;this.loading=false;this.error=true;this.message=e.error?.detail?.message||(e.status===401?'Entre com sua conta de RH para operar esta fila.':e.status===403?'Sua conta não tem acesso a esta empresa.':'Não foi possível confirmar a operação. Atualize a fila antes de tentar novamente.');}
 load():void {this.loading=true;forkJoin({list:this.api.list(),pending:this.api.pending(),ready:this.api.readiness(),areas:this.pulso.listAreas()}).subscribe({next:r=>{this.loading=false;this.connected=true;this.interventions=r.list;this.pending=r.pending;this.readiness=r.ready;this.areas=r.areas.filter(a=>!a.isAnonymized);if(!this.areaId)this.areaId=this.areas[0]?.id||'';if(this.selected)this.select(this.selected.id);},error:e=>{this.connected=false;this.interventions=[];this.pending={actions:[],tasks:[],asOf:''};this.selected=null;this.review=null;this.history=null;this.areas=[];this.fail(e);}});}
 select(id:string):void {forkJoin({item:this.api.get(id),history:this.api.history(id)}).subscribe({next:r=>{this.selected=r.item;this.history=r.history;this.review=null;},error:e=>this.fail(e)});}
 execute<T>(operation:Observable<T>,success:string,after?:(result:T)=>void):void {if(this.busy)return;this.busy=true;this.error=false;operation.subscribe({next:result=>{this.busy=false;this.message=success;after?.(result);this.load();},error:e=>this.fail(e)});}
 prepare():void {if(!this.areaId||!this.title.trim()||this.objective.trim().length<10)return;const body={areaId:this.areaId,title:this.title,objective:this.objective,firstTask:{kind:'TASK',title:this.taskTitle,dueAt:new Date(this.due).toISOString(),reminders:this.reminderChannel?{channel:this.reminderChannel,intervalDays:this.intervalDays,maxReminders:this.maxReminders}:null}};this.execute(this.api.prepare(body,this.key(body)),'Intervenção preparada. Revise a primeira tarefa antes de aprovar.',item=>this.selected=item);}
 prepareAction():void {if(!this.selected)return;let payload:unknown;if(this.actionKind==='TASK')payload={kind:'TASK',title:this.reevaluation?'Reavaliar indicadores e evidências da intervenção':this.taskTitle,dueAt:new Date(this.due).toISOString(),purpose:this.reevaluation?'REEVALUATION':'INTERVENTION'};else if(this.actionKind==='SLACK')payload={kind:'SLACK',channel:this.channel,template:'FOLLOW_UP'};else payload={kind:'CALENDAR',calendarId:this.calendar,startsAt:new Date(this.starts).toISOString(),endsAt:new Date(this.ends).toISOString(),timezone:this.timezone,attendees:this.attendees.split(',').map(x=>x.trim()).filter(Boolean)};const draftKey=JSON.stringify({intervention:this.selected.id,payload});if(!this.actionDrafts.has(draftKey))this.actionDrafts.set(draftKey,{payload,notBefore:new Date().toISOString()});const body=this.actionDrafts.get(draftKey)!;const stableKey=this.key({intervention:this.selected.id,body});this.execute(this.api.prepareAction(this.selected.id,body,stableKey),'Ação preparada. Revise o conteúdo e os destinatários antes de aprovar.');}
 inspect(action:RhAction):void {this.review=action;this.confirmation=false;}
 approve():void {if(!this.review||!this.confirmation)return;this.execute(this.api.approve(this.review),'Ação aprovada e colocada na fila. O resultado aparecerá após o worker confirmar a execução.',()=>this.review=null);}
 change(action:RhAction,operation:'cancelar'|'tentar-novamente'|'solicitar-revisao'):void {this.execute(this.api.change(action.id,operation),'Solicitação registrada. Confira o estado atualizado.');}
 record():void {if(!this.evidenceTask||this.evidenceText.trim().length<10)return;this.execute(this.api.evidence(this.evidenceTask.id,this.evidenceText,this.evidenceUrl),'Evidência registrada como declaração do RH.',()=>{this.evidenceTask=null;this.evidenceText='';this.evidenceUrl='';});}
 complete(task:RhTask):void {this.execute(this.api.complete(task.id),'Tarefa concluída com a evidência registrada pelo RH.');}
 cancelTask(task:RhTask):void {this.execute(this.api.cancelTask(task.id),'Tarefa cancelada. Lembretes ainda na fila foram cancelados.');}
 reconcile():void {if(!this.uncertain||this.reconciliationNote.trim().length<15||this.externalRef.trim().length<3)return;this.execute(this.api.reconcile(this.uncertain.id,{outcome:this.outcome,description:this.reconciliationNote,externalReference:this.externalRef}),'Conferência registrada com a sua autoria.',()=>this.uncertain=null);}
}
