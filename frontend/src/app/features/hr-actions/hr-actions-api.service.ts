import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
export interface Preview {
 title?:string; dueAt?:string; channel?:string; text?:string; calendarId?:string;
 summary?:string; description?:string; startsAt?:string; endsAt?:string; attendees?:string[];
 reminderPolicy?:{channel:string;intervalDays:number;maxReminders:number}|null;
 remindersPreview?:{scheduledAt:string;channel:string;text:string}[];
 scheduledReminders?:string[]; sendsExternally?:boolean; sendsInvitations?:boolean;
}
export interface RhAction {
 id:string; interventionId:string; kind:'TASK'|'SLACK'|'CALENDAR'; status:string;
 digest:string; preview:Preview; notBefore:string; availableAt:string; errorCode:string|null;
 receipt?:{provider:string;taskId?:string;eventId?:string;messageTs?:string;externalReference?:string}|null;
}
export interface RhTask {id:string;actionId:string;interventionId:string;title:string;dueAt:string;status:string;purpose:string;overdue?:boolean;}
export interface Intervention {id:string;areaId:string;title:string;objective:string;createdAt:string;actions?:RhAction[];tasks?:RhTask[];}
export interface Pending {actions:RhAction[];tasks:RhTask[];asOf:string;}
export interface Readiness {externalEnabled:boolean;slackConfigured:boolean;calendarConfigured:boolean;slackChannels:string[];calendars:string[];allowedAttendees:string[];}
export interface History {events:{id:string;eventType:string;createdAt:string}[];evidence:{id:string;description:string;url?:string;createdAt:string}[];}
export interface WorkerCycle {
 executadoEm:string;areasAnalisadas:number;cardsAbertos:number;
 cards:{cardId:string;areaId:string;area:string;nivel:string;fator:string;resultado:string;intervencaoId:string|null;avisoSlack:boolean;temAcaoDaEmpresa:boolean|null;lacunas:string[];motivo:string|null}[];
 pendenciasBase:{tipo:string;mensagem:string;responsavel:string|null;documentoId:string|null;versaoId:string|null;prazo:string|null;fator:string|null}[];
}
@Injectable({providedIn:'root'})
export class HrActionsApi {
 private http=inject(HttpClient); private base=environment.apiUrl+'/rh';
 cycle(){return this.http.post<WorkerCycle>(environment.apiUrl+'/worker/ciclo',{});}
 report(){return this.http.get(environment.apiUrl+'/worker/relatorio.pdf',{responseType:'blob'});}
 list(){return this.http.get<Intervention[]>(this.base+'/intervencoes');}
 pending(){return this.http.get<Pending>(this.base+'/pendencias');}
 readiness(){return this.http.get<Readiness>(this.base+'/conectores');}
 get(id:string){return this.http.get<Intervention>(`${this.base}/intervencoes/${id}`);}
 history(id:string){return this.http.get<History>(`${this.base}/intervencoes/${id}/historico`);}
 prepare(body:unknown,key:string){return this.http.post<Intervention>(this.base+'/intervencoes',body,{headers:{'Idempotency-Key':key}});}
 prepareAction(id:string,body:unknown,key:string){return this.http.post<RhAction>(`${this.base}/intervencoes/${id}/acoes`,body,{headers:{'Idempotency-Key':key}});}
 approve(action:RhAction){return this.http.post<RhAction>(`${this.base}/acoes/${action.id}/aprovar`,{expectedDigest:action.digest});}
 change(id:string,operation:'cancelar'|'tentar-novamente'|'solicitar-revisao'){return this.http.post<RhAction>(`${this.base}/acoes/${id}/${operation}`,{});}
 evidence(id:string,description:string,url?:string){return this.http.post(`${this.base}/tarefas/${id}/evidencias`,{description,url:url||null});}
 complete(id:string){return this.http.post(`${this.base}/tarefas/${id}/concluir`,{});}
 cancelTask(id:string){return this.http.post(`${this.base}/tarefas/${id}/cancelar`,{});}
 reconcile(id:string,body:unknown){return this.http.post<RhAction>(`${this.base}/acoes/${id}/reconciliar`,body);}
}
