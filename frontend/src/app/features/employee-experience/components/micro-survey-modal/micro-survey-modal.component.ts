import { Component, Input, Output, EventEmitter, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
@Component({selector:'app-micro-survey-modal',standalone:true,imports:[CommonModule],template:`
<div *ngIf="isOpen" class="survey-overlay"><section class="panel survey-dialog" role="dialog" aria-modal="true" aria-labelledby="survey-title"><header class="section-title"><div><p class="eyebrow">VYTAL.ai · Escuta da equipe</p><h2 id="survey-title">{{title}}</h2><p class="subtle">Responda sobre sua experiência de trabalho, sem identificar outras pessoas.</p></div><button class="btn outline" type="button" aria-label="Fechar pesquisa" (click)="onClose()">Fechar</button></header>
<fieldset *ngFor="let question of questions;let index=index" class="survey-question"><legend>{{question.title}}</legend><div class="survey-scale" role="group" [attr.aria-label]="question.title"><button *ngFor="let value of [1,2,3,4,5]" type="button" class="btn outline" [class.selected]="answer(index)===value" [attr.aria-pressed]="answer(index)===value" (click)="setAnswer(index,value)">{{value}}</button></div><div class="survey-labels"><span>{{question.low}}</span><span>{{question.high}}</span></div></fieldset>
<p class="subtle">As respostas devem ser analisadas de forma agregada, respeitando o mínimo de participantes.</p><footer class="decide"><button type="button" class="btn outline" (click)="onClose()">Cancelar</button><button type="button" class="btn purple" [disabled]="!complete()" (click)="onSubmit()">Enviar respostas</button></footer></section></div>`})
export class MicroSurveyModalComponent {
 @Input() isOpen=true;@Input() title='Pesquisa de bem-estar';@Output() closed=new EventEmitter<void>();@Output() submitted=new EventEmitter<{q1:number;q2:number;q3:number}>();
 q1Answer=signal<number|null>(null);q2Answer=signal<number|null>(null);q3Answer=signal<number|null>(null);
 questions=[{title:'Como você avalia o volume e o ritmo da sua carga de trabalho este mês?',low:'Muito pesada (1)',high:'Equilibrada (5)'},{title:'Você sente que dispõe do apoio necessário da sua liderança para suas entregas?',low:'Pouco apoio (1)',high:'Total apoio (5)'},{title:'O ambiente interpessoal do seu time tem sido respeitoso e acolhedor?',low:'Conflituoso (1)',high:'Harmonioso (5)'}];
 answer(index:number):number|null{return [this.q1Answer(),this.q2Answer(),this.q3Answer()][index];}
 setAnswer(index:number,value:number):void{[this.q1Answer,this.q2Answer,this.q3Answer][index].set(value);}
 complete():boolean{return [this.q1Answer(),this.q2Answer(),this.q3Answer()].every(value=>value!==null);}
 onClose():void{this.closed.emit();}
 onSubmit():void{const q1=this.q1Answer(),q2=this.q2Answer(),q3=this.q3Answer();if(q1===null||q2===null||q3===null)return;this.submitted.emit({q1,q2,q3});}
}
