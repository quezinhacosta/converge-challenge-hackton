# Ciclo do digital worker VytAI

O worker faz o trabalho de preparação. Quem decide e executa é sempre o RH.

```
fechamento → card amarelo/vermelho → investigação na base da empresa
          → proposta de intervenção na fila do RH (PENDENTE)
          → aviso neutro no Slack (PENDENTE, se houver canal)
          → revisão da base (pendências com responsável e prazo)
RH aprova/decide → execução pelo worker de ações → decisão vira memória citável na base
```

## O que cada etapa faz

| Etapa | Onde | Regra |
|---|---|---|
| Fechamento | `run_analysis_uc.execute_all()` | Score transparente; o LLM não decide o nível. |
| Investigação | `AssistenteDocumental.investigar` | O que a empresa já oferece, o que já tentou e o que falta. |
| Proposta | `ActionService.prepare_intervention` | O objetivo cita as fontes. Fica pendente até o RH aprovar. Um card gera uma única proposta, mesmo rodando o ciclo várias vezes. |
| Aviso no Slack | `SlackPayload(template="FOLLOW_UP")` | Texto neutro, sem objetivo, documentos ou dado de saúde. Também precisa de aprovação. |
| Compliance | `ASSEDIO` ou card escalado | Nunca entra na fila: segue o canal de compliance. |
| Cuidado da base | `revisar_base` | Documento vencendo, vencido, bloqueado, lacuna por fator, falta de canal de apoio. |
| Memória | resolução do card | A decisão vira `PLANO_ACAO_ANTERIOR` publicado. Roda num savepoint e nunca derruba a decisão. |

## Como disparar

- **RH na API:** `POST /api/v1/worker/ciclo`. Exige o papel RH.
- **MCP:** ferramentas `rodar_ciclo_do_worker` e `buscar_na_base_da_empresa`.
- **Agendador** (cron mensal, por exemplo dia 1 às 6h):

```bash
python -m app.digital_worker --once
```

O agendador usa `VYTAI_WORKER_EMPRESA_ID` e `VYTAI_WORKER_ACTOR_ID`, que precisam de vínculo RH ativo. Cada execução é uma transação, com isolamento por empresa.

## Demonstração (dados 100% sintéticos)

```bash
DATABASE_URL=<credencial de migração> python -m app.digital_worker.demo
```

O comando cria a empresa fictícia, o RH de demonstração, as áreas sintéticas e 5 documentos publicados. No final, ele imprime estas variáveis:

```
VYTAI_MODE=demo
VYTAI_DEMO_EMPRESA_ID=...
VYTAI_DEMO_USUARIO_ID=...
```

Com elas, uma requisição sem login vira o RH da empresa fictícia, e `/conhecimento`, `/acoes-rh` e o ciclo funcionam. Não use isso com dados reais: qualquer visitante age como esse RH.
