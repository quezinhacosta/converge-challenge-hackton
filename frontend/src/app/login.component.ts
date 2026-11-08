import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { SessionService } from './core/auth/session.service';
@Component({selector:'app-login',standalone:true,imports:[CommonModule,FormsModule],template:`
<header class="hero"><p class="eyebrow">VytAI · Acesso do RH</p><h1>Entre para acompanhar.</h1><p>Documentos, decisões e ações da sua empresa em um só lugar.</p></header>
<section class="panel panel-pad" style="max-width:480px;margin:24px auto"><h2>Acessar minha conta</h2><p class="notice error" *ngIf="message||session.error()" role="alert">{{message||session.error()}}</p>
<form (ngSubmit)="login()" *ngIf="!session.userEmail()" class="stack" style="margin-top:16px"><div><label for="login-email">Email corporativo</label><input id="login-email" type="email" name="email" [(ngModel)]="email" autocomplete="username" required maxlength="254"></div><div><label for="login-password">Senha</label><input id="login-password" type="password" name="password" [(ngModel)]="password" autocomplete="current-password" required maxlength="256"></div><button class="btn purple" type="submit" [disabled]="busy">{{busy?'Entrando…':'Entrar'}}</button><p class="subtle">O acesso é liberado pelo administrador do RH da empresa.</p></form>
<div *ngIf="session.userEmail()" class="stack" style="margin-top:16px"><p>{{session.userEmail()}}</p><ng-container *ngIf="session.companies().length"><label for="login-company">Selecione sua empresa</label><select id="login-company" [(ngModel)]="companyId"><option value="">Selecione</option><option *ngFor="let c of session.companies()" [value]="c.id">{{c.nome}}</option></select><button class="btn purple" [disabled]="!companyId" (click)="choose()">Continuar</button></ng-container><button class="btn outline" (click)="logout()">Usar outra conta</button></div></section>`})
export class LoginComponent {
 readonly session=inject(SessionService);private router=inject(Router);email='';password='';companyId='';busy=false;message='';
 constructor(){void this.session.restore().then(()=>{if(this.session.authenticated())void this.router.navigateByUrl('/');});}
 async login():Promise<void>{if(this.busy)return;this.busy=true;this.message='';try{await this.session.signIn(this.email,this.password);this.password='';if(this.session.authenticated())await this.router.navigateByUrl('/');}catch(error){this.password='';this.message=error instanceof Error?error.message:'Não foi possível entrar agora.';}finally{this.busy=false;}}
 choose():void{this.session.selectCompany(this.companyId);void this.router.navigateByUrl('/');}
 async logout():Promise<void>{await this.session.signOut();this.message='';}
}
