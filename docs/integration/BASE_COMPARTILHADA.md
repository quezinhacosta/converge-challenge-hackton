# Base compartilhada VytAI — Codex / Claude

Base de origem: `cae1bac52b68af001bd610d645fb3aef1f97dcca`. Implementacao em `feature/structured-data`, worktree isolada. Sem deploy, merge ou provisionamento externo.

## Estado oficial

A fabrica e `app.presentation.main:create_application`, entrypoint `app.presentation.main:app`. O alias `app.main:app` usa a mesma fabrica. Somente `/api/v1` executa casos de uso. As rotas legadas retornam 410; clientes devem migrar explicitamente. Funcoes Python antigas permanecem apenas para testes legados, sem exposicao HTTP.

`RiskCardDTO.from_entity` centraliza aliases e metadados. Decisao repetida e compliance retornam 409. CORS exige origens explicitas. O transporte Angular nao fabrica dados ou decisoes em falhas.

## Identidade e transacao

- `VYTAI_MODE=production` e o padrao: autenticação obrigatoria. Demo explicita (`VYTAI_MODE=demo`) usa memoria e seed sintetico. Nao usar demo com dados reais.
- `SUPABASE_JWT_ISSUER=https://<projeto>.supabase.co/auth/v1`; aceita JWT assimetrico ES256/RS256. Projetos com signing key HS256 antiga precisam migrar para chave assimetrica.
- `DATABASE_URL=postgresql+psycopg://...` somente no servidor; runtime exige TLS. Nao colocar credencial no Angular.
- O token identifica usuario; `empresa_usuario` resolve memberships e papel RH. `X-Empresa-Id` seleciona somente entre vinculos autorizados. Sem header, um unico vinculo e necessario.
- `ContextoAutorizado` esta em `app.application.contracts.identity`.
- Rotas documentais devem usar `Depends(require_authorized_context)` de `app.presentation.security`; `request_session` fornece a transacao com escopo de empresa. Use `Depends(request_session, scope="function")` e mantenha a mesma dependencia em toda a requisicao.
- Transacao fecha antes de enviar resposta HTTP. Falha de banco gera erro sanitizado; revisor produtivo vem da identidade autenticada.
- Repositorios produtivos nao executam seed. Filtro de empresa explicito e RLS; usar papel de aplicacao sem BYPASSRLS. Nao compartilhar acesso SQL com clientes. A migration cria `vytai_app` sem login/bypass; o engine aplica `SET ROLE vytai_app` a cada conexao. O operador deve autorizar o login de runtime a assumir esse papel; nao usar a conta de migration no runtime.
- A interface de sessao Angular ja envia bearer/header apenas para a URL da API. A tela/adaptador de login Supabase ainda precisa ser conectada antes de publicar o modo autenticado.

## Banco e migrations

Supabase/PostgreSQL foi escolhido; ainda depende de projeto/credenciais externos. Instale `backend/requirements.txt` e execute `python -m alembic upgrade head` em backend com credencial administrativa de migration e DATABASE_URL configurada. Nunca rodar migrations no startup HTTP.

Migration `0001_shared_foundation` cria:

- empresa, empresa_usuario;
- area, metrica_area, evento_area, risk_card, pgr_item, survey_summary, team_devolutiva, auditoria;
- documento, documento_versao, documento_arquivo, documento_trecho, documento_evento, rag_execucao.

Os nomes/colunas documentais seguem a proposta do Claude, com estas diferencas deliberadas:

1. Original em `documento_arquivo(empresa_id, versao_id, original)`, maximo 10 MiB; nao existe coluna original em documento_versao.
2. FKs compostas por empresa e indices de publicacao/deduplicacao. Hash unico entre versoes PRONTO; erros/bloqueios nao reservam permanentemente o conteudo.
3. `documento_trecho` possui titulo_indice/categoria_indice mantidos por triggers. Config FTS: `public.vytai_portuguese`; usar essa mesma regconfig em websearch_to_tsquery. Sem wrapper IMMUTABLE de unaccent.
4. documento_evento conserva IDs e auditoria sem FK de cascade para documento, para sobreviver a exclusao. Nao gravar texto ou valores sensiveis em detalhe.
5. Nenhum grant a anon/authenticated do Supabase. A API media o acesso. Nao criar pgvector ainda.
6. Downgrade destrutivo e bloqueado; mudancas posteriores por nova revisao Alembic.

O operador precisa provisionar empresas e memberships por canal administrativo antes do primeiro uso. Nao existe signup anonimo que crie permissao de RH.

## Integracao documental entregue

`app.presentation.knowledge_integration` expoe `KnowledgeIntegration(router, factory)`.

A montagem final sera:

```python
create_application(
    knowledge_integration=KnowledgeIntegration(
        router=router_do_claude,
        factory=criar_servicos_documentais,
    )
)
```

`factory(ctx, session)` recebe o contexto autenticado e a mesma SQLAlchemy Session da requisicao. Retorna servicos novos por chamada, com `chat_tools: tuple` e `finalize_chat(ChatQueryResponseDTO) -> ChatQueryResponseDTO`. A ferramenta captura ctx apenas nessa instancia. A finalizacao valida referencias e fidelidade antes de devolver citacoes.

Sem binding, `/api/v1/conhecimento/status` retorna indisponibilidade; nao simula cadastro. Quando o modulo estiver pronto, Codex conecta o binding no entrypoint e substitui o componente temporario da rota Angular `/conhecimento`. A rota ja existe e o shell usa router-outlet.

`CitacaoDTO` esta em `app.application.dtos.citation_dto`; nomes internos snake_case, API camelCase. Chat possui citacoes, card possui fontesDocumentais e evidenciaDocumentalSuficiente (null = nao avaliado). Entidade RiskCard e repositorio persistem os campos documentais.

`IndicadoresArea` e os tipos associados estao em `app.application.contracts.indicators`. Sao imutaveis, possuem snapshot/empresa/periodo/origem/versao e rejeitam classificacao quando nao ha quorum/elegibilidade. Decimais serializados como strings. O RAG nao altera score/nivel/fator. A integracao de fundamentacao dos cards aguarda os modulos e testes do Claude; nao esta declarada concluida.

## Avaliacoes e limites

- Calculos de variacao em `domain/services/indicator_calculator.py` distinguem ausente, incompleto e baseline zero.
- Runtime usa TransparentRiskEngine, versao rules-v1-demo; sao limiares operacionais de demonstracao, nao modelo treinado/SHAP ou validacao clinica. Regras de piloto exigem revisao especializada. Classe ML antiga permanece para compatibilidade de testes legados.
- Analise sem historico nao gera verde/card. Simulacao de reavaliacao e recusada em requisicoes produtivas.
- MCP stdio suporta token e empresa por processo; nao compartilhar processo entre identidades. Transporte HTTP multiusuario fica bloqueado em producao ate integrar autenticacao propria.
- Conector Tako, sincronizacao duravel, snapshots reais, cadastro documental, avaliacao RAG e login completo nao sao implementados por este commit de fundacao.
- Sem depender de Supabase para testes unitarios. Teste SQLite de repositorio e apenas test double; nao valida RLS.
- Testes PostgreSQL reais usam exclusivamente `VYTAI_TEST_DATABASE_URL` descartavel. A migration e aplicada nesse banco; nunca apontar para producao. A CI possui job PostgreSQL dedicado.

## Proximo merge do Claude

Claude mantem seus modulos exclusivos. Entregar router, factory request-scoped, schemas/repositorio documental e testes. Codex integra providers e cards, registra binding e atualiza rota, sem duas pessoas editarem compartilhados simultaneamente.


## Verificacao desta entrega

- 59 testes passaram, sem skips, incluindo PostgreSQL 17.11 temporario real.
- Migration aplicada em banco vazio; FTS com unaccent, FK entre empresas, RLS com papel sem bypass, exclusao em cascade e PGR apos nova sessao verificados.
- Build Angular de producao passou.
- Ruff dos arquivos Python alterados e MyPy do nucleo novo foram verificados.
- O banco temporario de teste foi encerrado. Nenhum servico produtivo foi alterado.
