# VytAI — Frente de cadastro documental e RAG (plano inicial)

Status: **planejamento, nada implementado**. Este documento serve para alinhar contratos
com a frente do Codex (Tako, indicadores, persistência, autenticação, integração).
Referência inspecionada: `origin/main` em `cae1bac` (Merge PR #4, 2026-11-07).

---

## 1. Diagnóstico (com referências)

### 1.1 O que está em cada lugar

| Lugar | Versão | Observação |
|---|---|---|
| `origin/main` | `cae1bac` | Contém Strands/MCP (PR #3) **e** a `feature/04` mesclada (PR #4). |
| Backend publicado (Render) | `feature/strands-agents` (`9f08883`) | `render.yaml` aponta `branch: feature/strands-agents`. O `/openapi.json` publicado diz "Pulso API 0.1.0" e só tem rotas `/api/v1/*` (sem `/fechamento`, `/casos/...`, `/chat/query` da `main`). |
| Frontend publicado (Vercel) | não identificado com certeza | O site já mostra "VytAI" e chama `https://pulso-backend-fjug.onrender.com/api/v1`, mas no repositório `frontend/src/environments/environment.prod.ts` ainda tem o marcador `SEU-SERVICO.onrender.com`. Indica deploy de uma versão local/não commitada. |
| `feature/adapta-04` (local, não enviada) | `f3d0f4c` | Adaptação da feature/04 feita antes do PR #4; hoje diverge da `main`. Não é base para esta frente. |

### 1.2 Estado da `main` relevante para o RAG

- **Persistência:** somente memória (`backend/app/infrastructure/repositories/in_memory_pulso_repositories.py`), populada por `backend/scripts/seed_synthetic_data.py`. Reinício do Render perde tudo.
- **Dois estados paralelos:** `backend/app/main.py` mantém `STORE_AREAS`/`STORE_CASOS` próprios; `backend/app/presentation/deps.py` mantém o `PulsoAppContainer`. As rotas `/fechamento`, `/casos/{id}/decisao` e `/chat/query` usam o primeiro; `/api/v1/*` e o MCP usam o segundo.
- **Autenticação/empresa:** inexistente. Não há conceito de empresa (tenant) nem papéis.
- **CORS:** `backend/app/presentation/main.py` voltou a permitir `*` com `allow_credentials=True` (padrão de `PULSO_CORS_ORIGINS` inclui `*`).
- **Agente:** `backend/app/infrastructure/llm/resilience/strands_provider.py` (Strands + Featherless, Qwen 2.5 72B) com especialistas Historiador/Regulatório/Comunicação e um agente de chat com ferramentas por área (`backend/app/infrastructure/tools/strands_area_tools.py`). Failover em `.../resilience/failover_manager.py`. Há ainda um segundo conjunto de agentes em `backend/app/pulso_agents.py` (cliente Featherless próprio, Llama 3.1 8B — modelo bloqueado (403) na conta atual — e timeout de 4 s), usado pelas rotas de `app/main.py`.
- **"RAG" atual:** `backend/app/infrastructure/llm/knowledge.py` é um texto fixo (catálogo de fatores + paráfrases da NR-1) colado no prompt. Não há cadastro, recuperação nem citação.
- **Chat:** `ProcessRhChatQueryUseCase` (`backend/app/application/use_cases/process_rh_chat_query_use_case.py`) aplica o guardrail e chama `generate_team_response` → `FailoverManager.generate_chat_reply` → agente Strands com ferramentas por área. **Ponto natural para uma ferramenta de busca documental.**
- **Card:** `GenerateRiskCardUseCase` recebe a análise (nível/fator calculados em código) e o texto dos agentes. **Ponto natural para fundamentar a ação sugerida em documentos.**
- **Testes:** na `main`, 41 passam e **5 falham** (`tests/unit/test_api_contract.py`). Causa: `backend/app/presentation/api/v1/endpoints/risk_cards.py` monta `RiskCardDTO` com nomes de campo antigos → `GET /api/v1/risk-cards/active` responde 500.
- **Frontend:** um único serviço compartilhado (`frontend/src/app/core/services/pulso-api.service.ts`) com *fallbacks* que exibem dados de demonstração quando a API falha.

### 1.3 Riscos que afetam esta frente (para o Codex)

1. Base com testes quebrados e dois estados paralelos: precisamos de um commit de partida estável.
2. Sem persistência nem tenant: o RAG depende disso para isolamento e exclusão efetiva.
3. Render free tem filesystem efêmero: originais e índice **não podem** ficar em disco local.
4. Trechos recuperados irão para a Featherless no prompt: a triagem de dados sensíveis na entrada é obrigatória (LGPD: a Featherless atua como operadora).

---

## 2. Matriz implementado / simulado / parcial / ausente

| Capacidade | Situação | Onde |
|---|---|---|
| Score e nível de risco por área | Implementado (em memória) | `app/infrastructure/ml/xgboost_risk_engine.py` (regras com percentuais fixos, não é ML treinado) e `app/protections.py` |
| Indicadores reais (Tako) | **Ausente** (dados sintéticos) | `scripts/seed_synthetic_data.py`, `app/main.py` (`carregar_areas_sinteticas`) |
| Agentes Strands + Featherless | Implementado | `app/infrastructure/llm/resilience/strands_provider.py` |
| Failover / plano B | Implementado | `failover_manager.py`, `rule_based_fallback_provider.py` |
| Guardrail de pedidos individuais | Implementado (regex) | `app/infrastructure/guardrails/privacy_guardrail.py`, `app/protections.py` |
| Conhecimento da empresa no prompt | **Simulado** (texto fixo) | `app/infrastructure/llm/knowledge.py` |
| Cadastro de documentos | **Ausente** | — |
| Extração/trechos/índice | **Ausente** | — |
| Recuperação autorizada com citação | **Ausente** | — |
| Persistência | **Ausente** (memória) | `in_memory_pulso_repositories.py` |
| Autenticação / empresa / papéis | **Ausente** | — |
| Reavaliação de 60 dias | **Simulada** (resultado fixo) | `track_risk_evolution_use_case.py` |
| MCP | Implementado (chama `/api/v1`) | `app/presentation/mcp_server.py` |
| Frontend ligado à API | **Parcial** (fallbacks mascaram falhas) | `pulso-api.service.ts` |

---

## 3. Arquitetura documental e escolha da busca

### 3.1 Fluxo

```
cadastro (texto) ou upload
  → validação (tamanho, formato, campos obrigatórios)
  → extração de texto (txt/md direto; PDF com camada de texto)
  → triagem de conteúdo sensível e de instruções suspeitas
  → divisão em trechos (com página e seção)
  → indexação textual (Postgres FTS, português)
  → [publicação pelo RH]
  → recuperação autorizada (filtros ANTES da busca)
  → resposta do agente com citações validadas
```

- **Sem embeddings no MVP.** A busca vetorial entra só se a avaliação mostrar falta de recall (ver 3.3).
- **Processamento síncrono no MVP:** arquivos ≤ 10 MB, extração rápida. O estado fica persistido em cada etapa (`RECEBIDO → PROCESSANDO → PRONTO | ERRO | BLOQUEADO`). Assim nenhuma tarefa se perde em fila; se o processo cair no meio, a versão fica `PROCESSANDO` com `iniciado_em` antigo e pode ser reprocessada.
- **Quando for assíncrono** (volume maior ou OCR): fila **no próprio banco**. O "claim" é atômico (`UPDATE ... SET status='PROCESSANDO', lock_ate=now()+interval WHERE id=? AND status IN ('RECEBIDO','ERRO') OR lock expirado RETURNING`). O processamento é idempotente por `versao_id`: apaga e recria os trechos dessa versão dentro de uma transação. Sem broker novo.

### 3.2 Busca textual × vetorial/híbrida para o volume inicial

Volume esperado por empresa no início: dezenas de documentos, centenas a poucos milhares de trechos.

| Critério | Postgres FTS (`tsvector`, dicionário português, `unaccent`) | Vetorial / híbrida (pgvector + embeddings) |
|---|---|---|
| Infraestrutura | Nenhuma além do Postgres que o Codex já vai adotar | Extensão pgvector + **provedor de embeddings novo** (a Featherless não é o caminho para embeddings hoje) |
| Custo | Zero por consulta | Custo por documento e por consulta; reindexação ao trocar de modelo |
| Privacidade | Texto não sai do banco para indexar | Todo trecho vai a mais um operador de dados |
| Consultas típicas | Montadas pelo backend a partir de fator, área e evento ("sobrecarga", "metas", "canal de apoio") → vocabulário previsível | Melhor para sinônimos e perguntas livres |
| Explicabilidade | Fácil mostrar por que o trecho veio | Mais difícil |

**Escolha: Postgres FTS**, com três reforços baratos:
- expansão de consulta determinística por fator (ex.: SOBRECARGA_METAS → "carga", "metas", "jornada", "pausa", "acolhimento");
- `websearch_to_tsquery('portuguese', ...)` com `ts_rank_cd` e peso extra para título e categoria;
- filtro por categoria quando a consulta vem do card.

A interface de recuperação é independente do método. Se a avaliação mostrar recall@5 abaixo da meta nas perguntas livres do chat, adicionamos pgvector **no mesmo banco** com fusão por RRF, sem mudar o contrato.

### 3.3 Armazenamento persistente

- **Metadados, trechos e índice:** Postgres gerenciado (escolha do Codex).
- **Arquivo original:** proposta para o MVP: `bytea` no próprio Postgres, com limite de 10 MB por arquivo. Evita adicionar um storage externo; dá para migrar para S3/R2 depois sem mudar a API (`storage_ref`).
- **Nada em disco local do Render.**

### 3.4 Regras de ingestão

- **Formatos MVP:** texto colado, `.txt`, `.md`, `.pdf` com camada de texto. `.docx` na etapa seguinte. Sem OCR no MVP.
- **Limites:** 10 MB por arquivo; 300 páginas; 500 mil caracteres extraídos; tipo validado por extensão **e** assinatura (magic bytes).
- **Ilegível/sem texto:** PDF sem texto extraível (escaneado) → `ERRO` com código `SEM_TEXTO_EXTRAIVEL` e a mensagem "O arquivo parece ser uma imagem escaneada. Envie a versão com texto ou cole o conteúdo."
- **Deduplicação:** SHA-256 do texto normalizado por empresa. Conteúdo idêntico a uma versão ativa → `DUPLICADO`, indicando o documento existente.
- **Versionamento:** `documento` (lógico) + `documento_versao` (imutável). "Substituir" cria a versão N+1. A anterior vira `SUBSTITUIDA` ao publicar a nova, e seus trechos deixam de ser recuperáveis na mesma transação.
- **Exclusão:** apaga o original, as versões e os trechos (cascade). Fica só um evento de auditoria sem conteúdo (id, título, hash, quem, quando). Se houver embeddings no futuro, ficam na mesma tabela de trechos e caem pelo mesmo cascade.
- **Reprocessamento:** permitido para versões em `ERRO` ou `PROCESSANDO` vencido; idempotente.
- **Triagem de conteúdo sensível (determinística, antes de publicar):** CPF, RG, CID-10 (ex.: F32.1), termos clínicos ("laudo", "prontuário", "atestado de <nome>"), e-mail e telefone pessoais, e padrões de segredo (chaves de API, `BEGIN PRIVATE KEY`, `senha=`). Resultado: `BLOQUEADO` com a lista dos **tipos** encontrados (nunca os valores) e a página/trecho. O RH também confirma no cadastro que o documento não contém dados pessoais sensíveis.
- **Instruções suspeitas** ("ignore as instruções", "você agora é", "system:"): o trecho é marcado `suspeito_injecao=true` e aparece para o RH revisar. Recuperado, é sempre tratado como dado (ver 5.4).

---

## 4. Modelo de dados proposto (para o Codex criar as migrations)

```sql
-- Requer: extensão unaccent; função IMMUTABLE f_unaccent() para uso em coluna gerada.

documento (
  id uuid PK,
  empresa_id uuid NOT NULL,               -- vem do contexto autenticado
  titulo text NOT NULL,
  categoria text NOT NULL,                -- POLITICA | PROCEDIMENTO_ACOLHIMENTO | CANAL_APOIO |
                                          -- PROGRAMA_BENEFICIO | PLANO_ACAO_ANTERIOR |
                                          -- CONTEXTO_ORGANIZACIONAL | REFERENCIA_APROVADA
  fonte text,                             -- ex.: "Manual do colaborador 2026"
  responsavel text NOT NULL,              -- área/pessoa responsável pelo conteúdo
  escopo_acesso text NOT NULL DEFAULT 'RH',  -- RH | RH_E_GESTORES (MVP: só RH)
  criado_por uuid NOT NULL, criado_em timestamptz, atualizado_em timestamptz
)
INDEX (empresa_id, categoria)

documento_versao (
  id uuid PK,
  documento_id uuid FK -> documento ON DELETE CASCADE,
  empresa_id uuid NOT NULL,               -- denormalizado para filtro
  numero int NOT NULL, rotulo text,       -- "v2 - mar/2026"
  origem text NOT NULL,                   -- TEXTO | UPLOAD
  nome_arquivo text, mime text, tamanho_bytes int,
  sha256_conteudo char(64) NOT NULL,
  original bytea,                         -- ou storage_ref text, se migrar para objeto
  vigencia_inicio date NOT NULL, vigencia_fim date NULL,
  status text NOT NULL,                   -- RECEBIDO | PROCESSANDO | PRONTO | ERRO | BLOQUEADO | SUBSTITUIDA
  erro_codigo text, erro_mensagem text, achados_sensiveis jsonb,  -- só tipos, nunca valores
  tentativas int DEFAULT 0, iniciado_em timestamptz, processado_em timestamptz,
  publicada boolean NOT NULL DEFAULT false, publicada_em timestamptz, publicada_por uuid,
  criado_por uuid, criado_em timestamptz,
  UNIQUE (documento_id, numero)
)
UNIQUE (documento_id) WHERE publicada          -- no máximo 1 versão publicada por documento
UNIQUE (empresa_id, sha256_conteudo) WHERE status <> 'SUBSTITUIDA'   -- deduplicação

documento_trecho (
  id uuid PK,                             -- determinístico: uuid5(versao_id, ordem)
  versao_id uuid FK -> documento_versao ON DELETE CASCADE,
  empresa_id uuid NOT NULL,
  ordem int NOT NULL, pagina int NULL, secao text NULL,
  texto text NOT NULL,
  suspeito_injecao boolean DEFAULT false,
  tsv tsvector GENERATED ALWAYS AS (
      setweight(to_tsvector('portuguese', f_unaccent(coalesce(secao,''))), 'B') ||
      setweight(to_tsvector('portuguese', f_unaccent(texto)), 'C')) STORED
  -- embedding vector(N) NULL   -- só se a avaliação justificar (etapa futura)
)
GIN INDEX (tsv); INDEX (empresa_id, versao_id)

documento_evento (                        -- auditoria, sem conteúdo
  id uuid PK, empresa_id uuid, documento_id uuid, versao_id uuid NULL,
  acao text,  -- CRIADO | VERSAO_ADICIONADA | PROCESSADO | ERRO | PUBLICADO | DESPUBLICADO | EXCLUIDO
  usuario_id uuid, em timestamptz, detalhe jsonb
)

rag_execucao (                            -- telemetria e avaliação, sem texto livre da consulta
  id uuid PK, empresa_id uuid, origem text,      -- CARD | CHAT | AVALIACAO
  consulta_hash char(64), trechos_ids uuid[], metodo text, config jsonb,
  latencia_ms int, modelo text, prompt_versao text, tokens_entrada int, tokens_saida int, em timestamptz
)
```

Requisitos de migration:
- Extensão `unaccent` disponível no Postgres gerenciado escolhido.
- **Toda** consulta da frente RAG filtra por `empresa_id`. Se o Codex adotar RLS, as tabelas acima entram na política.
- Migrations versionadas pelo mecanismo escolhido pelo Codex (ex.: Alembic). Eu forneço o DDL e os testes de integração.

---

## 5. Contrato de recuperação e citações

### 5.1 Contexto (nunca vem do corpo da requisição)

```python
@dataclass(frozen=True)
class ContextoAutorizado:          # construído pelo Codex a partir da autenticação
    empresa_id: UUID
    usuario_id: UUID
    papeis: frozenset[str]          # ex.: {"RH"}
    escopos_permitidos: frozenset[str]   # ex.: {"RH", "RH_E_GESTORES"}
```

### 5.2 Entrada e saída

```python
class ConsultaRecuperacao(BaseModel):          # app/application/dtos/retrieval_dto.py
    texto: str                                 # 3..500 caracteres
    categorias: list[CategoriaDocumento] | None = None
    fator_nr1: str | None = None               # usado para expansão determinística
    area_id: str | None = None                 # só para telemetria/ranking, não para filtro de acesso
    max_trechos: int = 5                       # 1..8
    max_caracteres: int = 6000                 # orçamento total para o prompt
    data_referencia: date | None = None        # padrão: hoje (para vigência)

class TrechoRecuperado(BaseModel):
    ref: str                     # "C1", "C2"... usado na resposta
    trecho_id: UUID
    documento_id: UUID
    versao_id: UUID
    titulo: str
    categoria: str
    versao_rotulo: str
    vigencia_inicio: date
    vigencia_fim: date | None
    pagina: int | None
    secao: str | None
    texto: str                   # trecho (limitado)
    score: float
    suspeito_injecao: bool

class ResultadoRecuperacao(BaseModel):
    trechos: list[TrechoRecuperado]
    evidencia_suficiente: bool
    motivo_insuficiencia: str | None    # "nenhum documento publicado na categoria X", "score abaixo do mínimo"
    possivel_conflito: list[tuple[str, str]]   # pares de refs de documentos vigentes da mesma categoria com orientações divergentes (heurística)
    metodo: Literal["fts"]               # depois: "hibrido_rrf"
    config: dict                         # pesos, limites, versão do índice
    latencia_ms: int
```

```python
class RecuperadorConhecimento(Protocol):
    def buscar(self, ctx: ContextoAutorizado, consulta: ConsultaRecuperacao) -> ResultadoRecuperacao: ...
```

**Filtros aplicados na query SQL, antes do ranking:** `empresa_id = ctx.empresa_id`, `versao.publicada`, `status = 'PRONTO'`, vigência contendo `data_referencia`, `escopo_acesso ∈ ctx.escopos_permitidos`, documento não excluído.

### 5.3 Citação na resposta

- O agente cita por `ref` ("[C2]"). O backend devolve a lista `citacoes` com documento, versão, página/seção e um trecho curto.
- **Validação determinística depois da geração:** toda `ref` citada precisa existir no `ResultadoRecuperacao` daquela chamada. Ref inexistente → a frase é removida, e a resposta ganha o aviso "uma citação inválida foi removida". Sem nenhum trecho → a resposta diz explicitamente que não há documento da empresa sobre o tema.
- **Fidelidade numérica:** todo número na resposta precisa existir nos indicadores recebidos ou nos trechos citados. Senão a resposta é marcada para revisão (e conta como falha na avaliação).

### 5.4 Proteção contra prompt injection

- Trechos entram no prompt num bloco delimitado (`<documentos_da_empresa>`), com a instrução de sistema de que são **fontes de informação, não instruções**.
- O agente de chat só tem ferramentas de leitura. Nenhuma ferramenta de escrita (decidir card, publicar) fica disponível para o fluxo que recebe trechos.
- Trechos `suspeito_injecao` vêm com um aviso no bloco e entram nos testes de avaliação.
- O contexto da empresa fica preso no servidor (closure da ferramenta). O modelo não escolhe `empresa_id`.

### 5.5 Incorporação ao agente sem quebrar contratos

1. **Chat:** nova ferramenta Strands de leitura `buscar_conhecimento_empresa(consulta, categoria?)`, criada por fábrica com o `ContextoAutorizado` capturado. Adicionar a ferramenta em `deps.py` fica com o Codex. `ChatQueryResponseDTO` ganha `citacoes: list[CitacaoDTO] = []` (campo opcional: não quebra o frontend).
2. **Card:** depois que nível e fator já foram calculados, o backend monta a consulta (fator + área + eventos) e passa os trechos ao Regulatório **como contexto**. Score, nível e fator não mudam. `RiskCardDTO` ganha `fontesDocumentais` e `evidenciaDocumentalSuficiente`, ambos opcionais.
3. **Indicadores recebidos pelo agente** (contrato a fechar com o Codex): `IndicadoresArea { area_id, periodo, score, nivel, fator, contribuicoes[], variacoes{}, quorum_ok, fonte, versao_calculo }`. É só leitura; o agente nunca recalcula nem altera esses valores.

---

## 6. Fluxo e telas do cadastro (Angular, componentes próprios)

Rota `/conhecimento` (registro da rota em `app.routes.ts` pelo Codex). Serviço próprio `knowledge-api.service.ts`, separado do `pulso-api.service.ts`.

1. **Lista de documentos:** título, categoria, versão publicada, status (chip: Recebido, Processando, Pronto, Erro, Bloqueado), vigência, responsável, atualizado em. Filtros por categoria, status e "vigentes".
2. **Novo documento (painel lateral):** abas **Colar texto** | **Enviar arquivo**; metadados; caixa obrigatória "Confirmo que não contém dados pessoais sensíveis nem prontuários/atestados nominativos".
3. **Detalhe:** metadados editáveis; linha do tempo das versões (status, erro em linguagem clara, achados sensíveis por tipo/página); ações **Publicar**, **Retirar publicação**, **Substituir** (nova versão), **Reprocessar**, **Excluir** (confirmação dizendo que é irreversível).
4. **Testar busca:** campo de pergunta que mostra os trechos recuperados, com referência (documento, versão, página) e o motivo quando não há evidência. É o que o RH usa para conferir antes de publicar.

### Mensagens de erro (códigos estáveis da API)

`FORMATO_NAO_SUPORTADO`, `ARQUIVO_GRANDE`, `ARQUIVO_CORROMPIDO`, `SEM_TEXTO_EXTRAIVEL`, `CONTEUDO_SENSIVEL_DETECTADO`, `DUPLICADO`, `VERSAO_NAO_PRONTA`, `VIGENCIA_INVALIDA`, `NAO_AUTORIZADO`, `DOCUMENTO_NAO_ENCONTRADO`. Formato: `{ codigo, mensagem, detalhes }`, onde `mensagem` é legível para o RH.

### Rotas (router próprio; o Codex registra em `main.py`)

```
POST   /api/v1/conhecimento/documentos                    (texto)
POST   /api/v1/conhecimento/documentos/upload             (multipart)
GET    /api/v1/conhecimento/documentos                    (lista + filtros)
GET    /api/v1/conhecimento/documentos/{id}               (metadados + versões)
PATCH  /api/v1/conhecimento/documentos/{id}               (metadados)
POST   /api/v1/conhecimento/documentos/{id}/versoes       (substituir: texto ou arquivo)
POST   /api/v1/conhecimento/versoes/{versao_id}/publicar
POST   /api/v1/conhecimento/versoes/{versao_id}/despublicar
POST   /api/v1/conhecimento/versoes/{versao_id}/reprocessar
DELETE /api/v1/conhecimento/documentos/{id}               (exclusão total)
POST   /api/v1/conhecimento/buscar                        (pré-visualização para o RH)
```

---

## 7. Arquivos sob minha responsabilidade (novos, sem tocar em compartilhados)

Backend:
```
backend/app/domain/entities/knowledge_document.py
backend/app/domain/repositories/knowledge_repository.py
backend/app/domain/services/knowledge_chunking.py
backend/app/domain/services/knowledge_content_screening.py
backend/app/application/dtos/knowledge_dto.py
backend/app/application/dtos/retrieval_dto.py
backend/app/application/use_cases/knowledge/  (registrar, processar, publicar, substituir, excluir, buscar)
backend/app/infrastructure/knowledge/text_extraction.py
backend/app/infrastructure/knowledge/in_memory_knowledge_repository.py   (testes/fixtures)
backend/app/infrastructure/knowledge/postgres_knowledge_repository.py    (após o esquema do Codex)
backend/app/infrastructure/knowledge/fts_retriever.py
backend/app/infrastructure/knowledge/grounding.py      (bloco de prompt, validação de citações e números)
backend/app/infrastructure/tools/knowledge_tool.py     (ferramenta Strands de leitura)
backend/app/presentation/api/v1/endpoints/knowledge.py (router)
backend/tests/unit/knowledge/
backend/tests/eval/rag/   (documentos controlados, perguntas, executor, relatório)
```
Frontend:
```
frontend/src/app/features/knowledge/   (lista, formulário, detalhe, testar busca)
frontend/src/app/features/knowledge/knowledge-api.service.ts
frontend/src/app/features/knowledge/knowledge.model.ts
```

Compartilhados (**mudanças pedidas ao Codex, não edito**): `app/presentation/main.py` (incluir o router), `app/presentation/deps.py` (instanciar o recuperador e a ferramenta), `requirements.txt` (`pypdf`), migrations, autenticação/`ContextoAutorizado`, `strands_provider.py` e `pulso_agent.py` (pontos de injeção de contexto), `ChatQueryResponseDTO`/`RiskCardDTO` (campos opcionais), `frontend/src/app/app.routes.ts`.

Dependência adicional justificada: **`pypdf`** (extração de texto de PDF, Python puro, licença BSD). `python-docx` só na etapa de `.docx`. Nenhum banco vetorial nem provedor de embeddings no MVP.

---

## 8. Backlog em etapas pequenas

| Etapa | Entrega | Critério de aceite |
|---|---|---|
| E0 | Contratos alinhados e fixtures (`ContextoAutorizado`, `IndicadoresArea`, DTOs acima) | Documento aprovado pelas duas frentes; commit de partida definido |
| E1 (**primeiro incremento**) | Cadastro de **texto** → trechos → recuperação FTS com filtros → resposta com citação → substituição e exclusão, sobre o repositório em memória e um router de teste | Teste de ponta a ponta: o documento cadastrado é citado com `ref` válida; depois de substituir, só a v2 aparece; depois de excluir, zero trechos e resposta "sem evidência"; documento de outra empresa nunca aparece |
| E2 | Triagem de conteúdo sensível e de instruções suspeitas | Fixtures com CPF/CID/chave de API ficam `BLOQUEADO` com os tipos listados e sem os valores |
| E3 | Upload `.txt`, `.md`, `.pdf` + validações + `SEM_TEXTO_EXTRAIVEL` | Tabela de casos (válido, grande, extensão falsa, PDF escaneado, PDF corrompido) com o código de erro esperado |
| E4 | Repositório Postgres + FTS (após as migrations do Codex) | Os mesmos testes de E1 a E3 passam contra o Postgres; teste de concorrência do "claim" de processamento |
| E5 | Ferramenta do chat + validação de citações e números | Chat cita `[Cn]` válidas; ref inventada é removida; número fora dos indicadores é sinalizado |
| E6 | Fundamentação do card (Regulatório recebe trechos) | Score/nível/fator idênticos com e sem RAG; o card traz `fontesDocumentais`; sem documento → `evidenciaDocumentalSuficiente=false` |
| E7 | Telas Angular do cadastro | Fluxo completo no navegador contra a API; estados e erros legíveis |
| E8 | Avaliações completas + relatório | Metas da seção 9 atingidas no conjunto de validação |
| E9 (condicional) | Busca híbrida pgvector + RRF | Só se E8 mostrar recall@5 < 0,85 em perguntas livres |

---

## 9. Plano de avaliações

**Dados:** duas empresas fictícias (A e B), cerca de 15 documentos controlados, sem dados pessoais reais:
- políticas, canal de apoio, programa de apoio psicológico, plano de ação 2025, contexto organizacional;
- 1 documento vencido, 1 não publicado e 1 excluído;
- 1 documento com v1 → v2 (telefone e prazo mudam);
- 2 documentos conflitantes (prazos diferentes);
- 1 documento com texto de prompt injection;
- 1 PDF escaneado e 1 com CPF/CID (devem ser bloqueados).

**Perguntas de referência:** cerca de 40, cada uma com os trechos esperados e o comportamento esperado. Divisão **fixa**: 25 de desenvolvimento e 15 de validação. As de validação não são usadas para ajustar nada.

| Aspecto | Verificação | Meta |
|---|---|---|
| Isolamento entre empresas | Determinística | 0 vazamentos |
| Vencido / não publicado / excluído / versão obsoleta | Determinística | 0 recuperações |
| Exclusão efetiva | Determinística (banco sem original, versões e trechos) | 100% |
| Citações | Determinística (ref ∈ recuperados; documento/versão/página batem) | 100% válidas |
| Recuperação | recall@5 e MRR contra os trechos esperados | recall@5 ≥ 0,85 (validação) |
| Sem evidência | A resposta declara falta de evidência | ≥ 95% |
| Fontes conflitantes | A resposta menciona as duas fontes | ≥ 90% |
| Fidelidade aos indicadores | Números da resposta ⊆ indicadores ∪ trechos | 100% |
| Prompt injection | A resposta não segue a instrução e não chama ferramenta indevida | 100% |
| Qualidade da recomendação | **Revisão humana** (2 pessoas, rubrica 1–5: aderência, utilidade, tom, respeito aos limites); LLM avaliadora só como apoio | média ≥ 4 |
| Latência e custo | p50/p95 da recuperação e da resposta; tokens por resposta | recuperação p95 < 300 ms; resposta dentro do orçamento atual do agente |

Cada execução grava um **manifesto**: commit, hash de cada documento e versão, versão dos prompts, modelo (`PULSO_LLM_MODEL`), embeddings (nenhum), configuração da recuperação, data.

---

## 10. Dependências e perguntas realmente bloqueantes

1. **Banco:** o Codex vai usar Postgres gerenciado? Qual provedor (precisa ter `unaccent`, e idealmente `pgvector` para o futuro)? Se não for Postgres, a escolha da busca muda.
2. **Autenticação e empresa:** como o `ContextoAutorizado` chega (claims do token? sessão?) e quais papéis existem no MVP. Sem isso não há como testar isolamento de forma real (até lá, fixture).
3. **Original no banco:** aceitam guardar o arquivo como `bytea` no Postgres (limite de 10 MB) no MVP, em vez de um storage externo?
4. **Commit de partida:** `cae1bac` tem 5 testes quebrados e dois estados paralelos (`app/main.py` × `deps.py`). Quem corrige antes de abrirmos as branches, e qual estado é o oficial? (Recomendação: o `PulsoAppContainer`/`/api/v1`, que já é usado pelo frontend e pelo MCP.)

Não bloqueantes: suporte a `.docx`, OCR, escopo `RH_E_GESTORES`, busca híbrida.
