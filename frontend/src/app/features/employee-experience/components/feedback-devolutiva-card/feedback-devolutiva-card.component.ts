import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
@Component({selector:'app-feedback-devolutiva-card',standalone:true,imports:[CommonModule],template:`
<article class="panel panel-pad"><header class="section-title"><div><p class="eyebrow">VYTAL.ai · Retorno à equipe</p><h2>O que ouvimos e o que vamos acompanhar</h2><p class="subtle">{{areaName||'Equipe'}}</p></div><span class="pill violet">Acompanhamento do RH</span></header><section class="block"><h3>O que foi identificado na escuta</h3><p style="margin-top:8px">{{listeningSummary||'O resumo será apresentado após a revisão do RH.'}}</p></section><section class="context block"><h3>Medida registrada pelo RH</h3><p style="margin-top:8px">{{actionPlan||'Nenhuma medida foi informada nesta consulta.'}}</p></section><footer class="subtle block">Este retorno trata da equipe. O acompanhamento da execução e dos resultados permanece na fila do RH.</footer></article>`})
export class FeedbackDevolutivaCardComponent {
 @Input() areaName='';@Input() listeningSummary='';@Input() actionPlan='';
}
