# Roteiro do Pitch e Guia de Demonstracao (3 Minutos)

Produto: Pulso - Digital Worker de Gestao de Riscos Psicossociais (NR-1) para o RH
Desafio: Converge Challenge powered by Tako | Desafio Tako: Digital Workers para RH
Equipe: Time Booleanas

---

## 1. Estrutura Temporal do Pitch (Cronometro)

| Tempo | Bloco | Objetivo Principal |
| :--- | :--- | :--- |
| 0:00 - 0:45 | O Problema & A Dor da NR-1 | Apresentar a obrigacao legal (maio/2026), passivos trabalhistas e a dispersao dos dados nos sistemas. |
| 0:45 - 1:30 | O Produto Pulso & Guardrails | Explicar o papel do analista digital, o ciclo de 9 etapas e os limites inegociaveis (so areas, nunca pessoas; decisao com humanos). |
| 1:30 - 2:30 | Demonstracao ao Vivo na Tela | Mostrar os cenarios na interface Angular: Atendimento (Sobrecarga), Logistica (Lideranca), Chat (Guardrail Carla) e PGR. |
| 2:30 - 3:00 | Modelo de Negocio & Encaixe Tako | Precificacao SaaS B2B (R$ 4 a R$ 8/vida/mes), integracao com suites de RH/folha e fechamento de impacto. |

---

## 2. Roteiro de Fala Segundo a Segundo

### [0:00 - 0:45] O Contexto e a Dor do Mercado
"A NR-1 obriga toda empresa CLT a gerenciar risco psicossocial desde maio de 2026. Mas hoje, a maioria cumpre essa regra com um questionario anual e um relatorio generico de consultoria que vira PDF e e esquecido na gaveta.

O resultado? O RH so descobre que um time esta adoecendo quando chega o pedido de demissao em massa, o afastamento longo por saude mental ou o processo trabalhista milionário. O problema vira caro antes de virar visivel.

Os sinais desse adoecimento ja existem nos sistemas da empresa: atestados estao no DP, desfalques e horas extras estao no ponto, desligamentos estao no RH e denuncias estao no canal de compliance. Os dados ja mostram onde esta o problema. O drama e que ninguem esta olhando para eles juntos."

---

### [0:45 - 1:30] A Solucao: O Pulso
"Para resolver isso, criamos o Pulso: o digital worker que atua como o analista de riscos psicossociais da NR-1 para o time de RH.

Ele roda de forma continua a cada fechamento de folha. O Pulso cruza esses sinais operacionais, compara com o historico da propria area e com a media da empresa, correlaciona com eventos reais (como uma nova meta agressiva ou a troca de lideranca) e redige um Ponto Focal de Atencao em linguagem simples.

E aqui esta o diferencial que nenhum dashboard tradicional tem: os limites eticos do Pulso fazem parte do produto, nao sao aviso de rodape:
1. O Pulso olha exclusivamente para times e areas, nunca para individuos.
2. Grupos com menos de 5 pessoas tem dados ocultados para impedir identificacao por exclusao.
3. Dados sensiveis de saude como CID e diagnosticos sao sumariamente descartados.
4. E a regra de ouro: o agente prepara, sugere a acao, mas quem decide e sempre uma pessoa do RH."

---

### [1:30 - 2:30] Demonstracao ao Vivo na Interface Angular
*(Tela compartilhada no navegador em http://localhost:4200)*

1. **Card de Sobrecarga (Atendimento ao Cliente)**:
   - "Aqui na tela, vemos o Cockpit de Governanca do RH. O Pulso detectou um Card Vermelho de Atencao Alta no Atendimento ao Cliente.
   - Ele aponta com precisao: dias de atestado subiram 45%, horas extras subiram 60% e houve 4 pedidos de demissao.
   - O agente cruzou com o contexto: essa alta comecou exatamente 2 semanas apos a implantacao da nova meta de atendimentos por hora.
   - Em vez de apenas gerar um grafico, o Pulso propoe a acao: revisar a meta com a lideranca e mediar uma conversa de escuta.
   - Em 1 clique, eu clico em 'Aprovar e registrar no PGR'. Automaticamente, o risco e formalizado no inventario da NR-1 com reavaliacao em 60 dias e o Pulso dispara o comunicado de devolutiva para o time: 'Voce falou, a empresa fez'."

2. **Teste do Guardrail Etico no Chat**:
   - "Agora vamos testar os limites do agente no console de chat. Se eu perguntar: 'Como esta o time de Logistica?', ele me responde com metricas agregadas da area, apontando que a troca de gestor em setembro gerou um sinal amarelo.
   - Mas se eu tentar quebrar a privacidade e pedir: 'Me mostra os atestados da Carla', o guardrail etico recusa imediatamente, explicando que atua somente no nivel coletivo e cumpre a LGPD."

3. **Anonimizacao de Grupo Pequeno (Aba Visao de Areas)**:
   - "Ao acessar a visao de areas, notem o time de Design com apenas 3 pessoas: para impedir exposicao de pessoas por exclusao, o Pulso oculta os graficos e exibe o alerta de protecao por anonimizacao."

4. **Fechamento do Ciclo (Acompanhamento de 60 Dias)**:
   - "Na tabela do PGR, ao clicar em 'Reavaliar (60 dias)', o agente afere a queda de 35% nos atestados, valida a eficacia da acao e encerra o ciclo formal de conformidade."

---

### [2:30 - 3:00] Negocio, Encaixe com a Tako e Conclusao
"O modelo de negocio do Pulso e SaaS B2B, cobrando de R$ 4 a R$ 8 por colaborador/mes, ou como modulo add-on para suites corporativas de folha e RH.

O encaixe com a Tako e perfeito: plataformas de RH e folha ja guardam os dados de ponto, afastamentos e demissoes. O Pulso e a camada de inteligencia que transforma esse passivo de dados em conformidade legal com a NR-1 e retencao de talentos.

Com o Pulso, a empresa cumpre a lei com dados reais, protege seus colaboradores do adoecimento mental e para de descobrir problemas quando ja viraram processos trabalhistas.

Muito obrigado!"

---

## 3. Checklist Tecnico para Gravacao da Demo

- [ ] Backend FastAPI rodando na porta 8000 (`uvicorn app.presentation.main:app --port 8000`)
- [ ] Frontend Angular rodando na porta 4200 (`npm start`)
- [ ] Navegador aberto e maximizado em tela limpa (sem favoritos visiveis)
- [ ] Teste de som e microfone com fala pausada e clara
- [ ] Tempo cronometrado para nao ultrapassar 3 minutos (cravado entre 2m45s e 2m55s)
