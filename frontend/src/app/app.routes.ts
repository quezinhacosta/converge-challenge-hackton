import { Routes } from '@angular/router';
export const routes: Routes = [
  { path: '', pathMatch: 'full', loadComponent: () => import('./dashboard.component').then(m => m.DashboardComponent) },
  { path: 'conhecimento', loadComponent: () => import('./features/knowledge/knowledge-page.component').then(m => m.KnowledgePageComponent) },
  { path: 'acoes-rh', loadComponent: () => import('./features/hr-actions/hr-actions.component').then(m => m.HrActionsComponent) },
  { path: '**', redirectTo: '' },
];
