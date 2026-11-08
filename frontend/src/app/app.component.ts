import { Component, effect, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SessionService } from './core/auth/session.service';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
@Component({
 selector:'app-root',standalone:true,imports:[CommonModule,RouterOutlet,RouterLink,RouterLinkActive],
 template:`<a class="skip" href="#principal">Ir para o conteúdo</a><div class="app">
 <aside class="side" aria-label="Navegação principal">
  <a class="brand" routerLink="/" aria-label="VYTAL.ai, início">
   <svg aria-hidden="true" width="34" height="29" viewBox="0 0 88 76"><path d="M3 2H22Q25 2 25 5V16Q25 21 29 25L40 36Q44 40 48 36L59 25Q63 21 63 16V5Q63 2 66 2H85Q88 2 88 5V24Q88 27 85 27H74Q69 27 65 31L59 37Q55 41 55 47V69Q55 73 51 73H37Q33 73 33 69V47Q33 41 29 37L23 31Q19 27 14 27H3Q0 27 0 24V5Q0 2 3 2Z" fill="#7D39EB"/><rect x="66" y="55" width="18" height="18" rx="4" fill="#C6FF33"/></svg>
   <div><b>VYTAL.ai</b><small>DIGITAL WORKER · RH</small></div>
  </a>
  <nav><p class="nav-title">Governança</p>
   <a routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{exact:true}" ariaCurrentWhenActive="page">◫ <span>Visão executiva</span></a>
   <a routerLink="/" fragment="deliberacao">◇ <span>Fila de deliberação</span></a>
   <a routerLink="/acoes-rh" routerLinkActive="active" ariaCurrentWhenActive="page">↗ <span>Ações do RH</span></a>
   <a routerLink="/" fragment="setores">◉ <span>Matriz de setores</span></a>
   <a routerLink="/" fragment="inventario">▤ <span>Inventário PGR</span></a>
   <a routerLink="/conhecimento" routerLinkActive="active" ariaCurrentWhenActive="page">▥ <span>Base de conhecimento</span></a>
  </nav>
  <div class="side-foot"><strong>{{session.company()?.nome||'RH / SESMT'}}</strong><span>{{session.demo()?'Demonstração · dados sintéticos':session.userEmail()}}</span><button *ngIf="session.userEmail()&&!session.demo()" class="btn outline" (click)="logout()">Sair da conta</button></div>
 </aside>
 <main id="principal" class="main" tabindex="-1"><router-outlet /></main>
 </div>`
})
export class AppComponent { readonly router=inject(Router);readonly session=inject(SessionService);constructor(){effect(()=>{if(this.session.ready()&&!this.session.authenticated()&&this.router.url!=='/entrar')void this.router.navigateByUrl('/entrar');});}async logout():Promise<void>{await this.session.signOut();await this.router.navigateByUrl('/entrar');} }
