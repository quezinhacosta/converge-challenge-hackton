import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
@Component({
  standalone: true, imports: [RouterLink],
  template: `<main class="max-w-2xl mx-auto p-8"><h1 class="text-2xl font-bold">Base de conhecimento</h1>
  <p class="my-4">O cadastro de documentos ainda não está disponível.</p>
  <a routerLink="/">Voltar ao painel</a></main>`,
})
export class KnowledgeUnavailableComponent {}
