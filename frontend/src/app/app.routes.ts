import { Routes } from '@angular/router';
import { authGuard } from './core/auth/auth.guard';
export const routes: Routes = [
  {path:'entrar',loadComponent:()=>import('./login.component').then(m=>m.LoginComponent)},
  { path: '', pathMatch: 'full', canActivate:[authGuard], loadComponent: () => import('./dashboard.component').then(m => m.DashboardComponent) },
  { path: 'conhecimento', canActivate:[authGuard], loadComponent: () => import('./features/knowledge/knowledge-page.component').then(m => m.KnowledgePageComponent) },
  { path: 'acoes-rh', canActivate:[authGuard], loadComponent: () => import('./features/hr-actions/hr-actions.component').then(m => m.HrActionsComponent) },
  { path: '**', redirectTo: '' },
];
