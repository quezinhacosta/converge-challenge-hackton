# Integração da base de conhecimento (para a frente de integração)

Pacote isolado em `backend/app/knowledge/`. Não altera arquivos compartilhados.
Testes: `pytest tests/unit/knowledge` (25 testes, sem rede).

## Composição (deps.py / main.py — responsabilidade da integração)

```python
from app.knowledge import api as conhecimento_api
from app.knowledge.grounding import RespondedorFundamentado
from app.knowledge.llm import GeradorTextoStrands
from app.knowledge.retrieval import RecuperadorTextual
from app.knowledge.service import ServicoConhecimento

# Singletons compartilháveis (não guardam empresa):
servico = ServicoConhecimento(repositorio, armazenamento)   # Postgres na etapa E4
recuperador = RecuperadorTextual(repositorio)                # ou FTS Postgres (mesmo Protocol)
respondedor = RespondedorFundamentado(recuperador, GeradorTextoStrands.criar_se_configurado())

app.include_router(conhecimento_api.router, prefix="/api/v1/conhecimento", tags=["Conhecimento"])
app.dependency_overrides[conhecimento_api.obter_contexto_conhecimento] = <dependência de auth>
app.dependency_overrides[conhecimento_api.obter_servico_conhecimento] = lambda: servico
app.dependency_overrides[conhecimento_api.obter_recuperador_conhecimento] = lambda: recuperador
app.dependency_overrides[conhecimento_api.obter_respondedor_conhecimento] = lambda: respondedor
```

Sem override, as rotas respondem 401 (contexto) ou 503 (componentes): nunca aceitam empresa do cliente.

## Chat (ferramenta por requisição)

```python
from app.knowledge.tool import criar_ferramenta_conhecimento
ferramenta = criar_ferramenta_conhecimento(recuperador, ctx)   # ctx = ContextoAutorizado DESTA requisição
```
Criar a cada requisição e passar ao agente Strands do chat junto das ferramentas por área.
Nunca guardar a ferramenta num singleton.

## Card

Depois que nível e fator já foram calculados:
```python
resposta = respondedor.responder(ctx, PerguntaRequest(pergunta=...), indicadores, fator_nr1=fator)
```
`indicadores`: lista de `IndicadorReferenciavel` (projeção do `IndicadoresArea` v1, com `valor`
já como string decimal). Persistir `resposta.citacoes` no card (snapshot) e
`evidencia_documental_suficiente = resposta.evidencia_suficiente and not resposta.resposta_segura`.
O RAG não altera score, nível, fator nem indicadores.

## Regras implementadas

- Filtros antes do ranking: empresa, versão publicada, `PRONTO`, vigência, escopo, categoria.
- Relevância por cobertura dos termos da pergunta; BM25 só ordena.
- Sem evidência: resposta segura, sem chamar o LLM.
- Citação `[Cn]` inexistente remove a frase; a resposta é revalidada e, sem suporte, vira resposta segura.
- Indicador só por marcador `{{ind:codigo}}` (preenchido pelo backend com métrica, área, período e unidade).
  Outro número só se estiver igual no trecho citado na mesma frase.
- Triagem antes de publicar: CPF válido, CID, documento clínico nominativo e segredos → `BLOQUEADO`,
  com original e trechos removidos; ficam só os códigos.
- Texto parecido com instrução: trecho marcado e tratado como dado no prompt.
- Exclusão efetiva: original, versões e trechos; auditoria sem título nem conteúdo.
- Processamento idempotente (ids de trecho determinísticos) com claim atômico e retomada de lock vencido.

## Pendências desta frente

- E3: upload `.txt/.md/.pdf` (`pypdf`) com limite durante a leitura, timeout e concorrência da extração.
- E4: repositório Postgres + FTS (trigger de `tsvector`, sem wrapper IMMUTABLE), sobre as migrations.
- E7: telas Angular `features/knowledge`.
- E8: conjunto de avaliação (desenvolvimento × validação) e relatório.
