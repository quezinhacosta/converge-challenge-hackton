import { Routes } from '@angular/router';
export const routes: Routes = [
  { path: '', pathMatch: 'full', loadComponent: () => import('./dashboard.component').then(m => m.DashboardComponent) },
  // Substituir este componente no merge da frente documental.
  { path: 'conhecimento', loadComponent: () => import('./knowledge-unavailable.component').then(m => m.KnowledgeUnavailableComponent) },
  { path: 'acoes-rh', loadComponent: () => import('./features/hr-actions/hr-actions.component').then(m => m.HrActionsComponent) },
  { path: '**', redirectTo: '' },
];
