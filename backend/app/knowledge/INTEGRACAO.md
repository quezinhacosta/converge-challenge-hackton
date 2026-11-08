# Integração da base de conhecimento (para o Codex)

Pacote isolado em `backend/app/knowledge/`, já sobre a base `feature/structured-data`
(contratos `ContextoAutorizado`, `CitacaoDTO`, `IndicadoresArea`, `KnowledgeIntegration`).
Nenhum arquivo compartilhado foi alterado.

## Montagem (entrypoint — Codex)

```python
from app.knowledge.api import router as router_conhecimento
from app.knowledge.integration import criar_servicos_documentais

create_application(knowledge_integration=KnowledgeIntegration(
    router=router_conhecimento,
    factory=criar_servicos_documentais,   # (ctx, session) -> ServicosDocumentais novos
))
```

- O router usa `require_authorized_context` e `Depends(request_session, scope="function")`.
  Sem binding: 503. Sem identidade: 401. Sem papel RH: 403.
- A factory usa `RepositorioConhecimentoSQL(session)` (repositório e armazenamento do
  original em `documento_arquivo`). Nunca faz commit: a transação é da requisição.
- `fabrica_em_memoria()` existe só para testes e demonstração local.

## Chat

`servicos.chat_tools` traz a ferramenta `buscar_conhecimento_empresa`, criada por requisição
(as refs `C1..Cn` são únicas entre chamadas da mesma requisição). Depois da resposta do agente:

```python
resposta = servicos.finalize_chat(resposta)
```

- Remove a frase que cita `[Cn]` inexistente nesta requisição.
- Numa frase com citação, todo número precisa estar no trecho citado.
- Frases sem citação documental (ex.: dados de área de outras ferramentas) ficam intactas.
- Preenche `citacoes` (CitacaoDTO) e acrescenta `base_conhecimento` em `sources_used`.

## Card (fundamentação)

Depois que nível e fator já foram calculados:

```python
from app.knowledge.indicadores import indicadores_para_prompt
ind = indicadores_para_prompt(indicadores_area, area_nome)       # [] se não elegível
inv = servicos.assistente.investigar(ctx, fator, area_nome, eventos)
resp = servicos.respondedor.responder(ctx, PerguntaRequest(pergunta=...), ind, fator_nr1=fator)
card.fontes_documentais = resp.citacoes                               # snapshot persistido
card.evidencia_documental_suficiente = resp.evidencia_suficiente and not resp.resposta_segura
```

O RAG não altera score, nível, fator nem indicadores.

## Digital worker (determinístico, sem LLM)

`servicos.assistente` (`AssistenteDocumental`):

| Método | Uso |
|---|---|
| `investigar(ctx, fator, area, eventos)` | Antes de montar o caso: programas, canais e procedimentos da empresa, planos anteriores, políticas e lacunas, com refs para citar. |
| `revisar_base(ctx, dia)` | Pendências da base: `VENCENDO`, `VENCIDO_PUBLICADO`, `PRONTO_SEM_PUBLICAR`, `ERRO_PROCESSAMENTO`, `BLOQUEADO_SENSIVEL`, `LACUNA_FATOR`, `SEM_CANAL_DE_APOIO`, com responsável e prazo. O agendador pode transformar cada uma em tarefa. |
| `registrar_decisao(ctx, ...)` | Depois da decisão do RH: vira documento `PLANO_ACAO_ANTERIOR` publicado e citável (passa pela triagem; dado pessoal bloqueia). |

Rotas: `GET /status`, `GET /pendencias`, `GET /investigar?fator=...`, além do CRUD de documentos,
`POST /buscar` e `POST /responder`.

## Pendências para o Codex

- MyPy acusa `app/application/dtos/risk_card_dto.py:74` (`fontes_documentais` recebe
  `list[dict]` onde o tipo é `list[CitacaoDTO]`). Arquivo do Codex.
- Registrar o binding acima, ligar `chat_tools` e `finalize_chat` no fluxo do chat e a
  fundamentação no card.
- Agendar `revisar_base` e encaminhar as pendências (Slack/tarefas).

## Testes

- `pytest tests/unit/knowledge` — sem rede e sem banco.
- `tests/integration/test_knowledge_postgres.py` — Postgres real descartável em
  `VYTAI_TEST_DATABASE_URL` (migration, RLS entre empresas, FTS, publicação/substituição,
  exclusão em cascata, claim concorrente). Nunca apontar para produção.
