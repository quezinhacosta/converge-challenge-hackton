# Pulso

Digital worker de gestao de riscos psicossociais (NR-1) para o RH
Converge Challenge powered by Tako | Desafio Tako: Digital Workers para RH | Time Booleanas

---

## Em uma frase
O Pulso cruza dados que o RH ja tem (atestados, desfalques, desligamentos, horas extras, canal de denuncias e pesquisas de clima), encontra as areas da empresa onde ha sinal de risco a saude mental, explica o porque, propoe uma acao e registra tudo no inventario de riscos exigido pela NR-1. Ele olha para times, nunca para individuos, e quem decide e sempre uma pessoa do RH.

### Frase de pitch
"A NR-1 obriga sua empresa a gerenciar risco psicossocial desde maio de 2026. Seus dados ja mostram onde esta o problema. Ninguem esta olhando para eles juntos."

---

## 1. O contexto: o que e a NR-1 e o que mudou
A NR-1 e a Norma Regulamentadora nº 1 do Ministerio do Trabalho e Emprego (MTE), a norma-base de seguranca e saude no trabalho. Ela obriga toda empresa com empregados CLT a manter um Gerenciamento de Riscos Ocupacionais (GRO), documentado no Programa de Gerenciamento de Riscos (PGR): identificar os riscos do trabalho, avaliar, agir e acompanhar.

A Portaria MTE nº 1.419/2024 incluiu expressamente os fatores de risco psicossociais nesse gerenciamento. Exemplos: sobrecarga e metas excessivas, jornadas longas, assedio moral e sexual, ma gestao e conflitos com a lideranca, falta de clareza de papel, falta de autonomia e inseguranca.

| Data | Marco |
| :--- | :--- |
| Ago/2024 | Publicacao da Portaria MTE nº 1.419/2024 |
| Mai/2025 | Portaria MTE nº 765/2025 adia a vigencia em um ano |
| 26/05/2026 | Vigencia: a gestao de riscos psicossociais passa a ser exigivel |
| Fim de ago/2026 | Termina o periodo de dupla visita (orientativo). O descumprimento pode gerar auto de infracao |

Alem da multa, a falta de gestao desses riscos pesa contra a empresa em acoes judiciais por doencas mentais ligadas ao trabalho. E o proprio MTE indica que campanhas genericas de bem-estar nao bastam: e preciso mapeamento com dados e evidencia documentada.

---

## 2. O problema
Os sinais de adoecimento de uma equipe ja existem nos sistemas da empresa, mas estao espalhados e ninguem os cruza:
- Atestados e afastamentos ficam no DP e na folha.
- Desfalques (faltas, coberturas, escalas descobertas) ficam no ponto e com o gestor.
- Desligamentos e entrevistas de saida ficam no RH, muitas vezes em planilha.
- Horas extras e banco de horas ficam no ponto e na folha.
- Denuncias de assedio ficam no canal de compliance.
- Clima e experiencia ficam numa pesquisa anual que vira PDF e e esquecida.

Hoje, a maioria das empresas cumpre a NR-1 com um questionario anual e um documento generico feito por consultoria. O resultado: o RH so descobre que um time esta adoecendo quando chega o pedido de demissao em massa, o afastamento longo ou o processo trabalhista. O problema vira caro antes de virar visivel.

| Pergunta do guia | Resposta |
| :--- | :--- |
| Qual e a dor? | Obrigacao legal nova (NR-1) sem ferramenta para cumprir com dados, mais o custo do adoecimento: afastamentos, turnover, processos. |
| Quem sofre? | RH, DP e SESMT de toda empresa com CLT. Quem paga: diretoria de pessoas e juridico. |
| Como se resolve hoje? | Questionario anual, consultoria pontual, planilha e percepcao do gestor. |
| Por que agora? | A NR-1 e exigivel e fiscalizada desde 2026, e LLMs conseguem cruzar fontes baguncadas, explicar padroes em linguagem simples e redigir o registro para o PGR. |

---

## 3. A solucao: o Pulso
O Pulso e um digital worker com papel definido: analista de riscos psicossociais do RH. Ele roda de forma continua (por exemplo, a cada fechamento de folha) e executa o ciclo de gerenciamento de riscos da NR-1 de ponta a ponta, parando na aprovacao humana.

### 3.1 As fontes de dados (os sinais)

| Sinal | O que o Pulso le | O que ele nunca le |
| :--- | :--- | :--- |
| Atestados | Quantidade e dias de atestado por area e por mes | CID, diagnostico, nome do medico |
| Desfalques | Faltas, coberturas feitas por colegas, escalas descobertas | Motivo pessoal da falta |
| Desligamentos | Turnover, pedidos de demissao, temas das entrevistas de saida (agregados) | Falas identificaveis |
| Horas extras | Media de horas extras, banco de horas, intervalos nao cumpridos | - |
| Assedio | Numero de denuncias por area e tipo, em contagem | Conteudo da denuncia e envolvidos (fica com compliance) |
| Burnout e saude mental | Afastamentos longos por saude, so como contagem agregada vinda do SESMT | Qualquer dado individual de saude |
| Experiencia do colaborador | Pesquisas pulso curtas e anonimas, comentarios livres agregados | Respostas ligadas a nome |
| Contexto | Mudanca de gestor, nova meta, reestruturacao, contratacoes | - |

### 3.2 O ciclo do agente (9 etapas)

1. Coletar: Consulta as ferramentas (ponto, folha, desligamentos, canal de denuncias, pesquisas) e agrega tudo por area.
2. Anonimizar: Oculta qualquer grupo com menos de 5 pessoas e descarta dados de saude individuais.
3. Comparar: Compara cada area com o proprio historico (ultimos 3 a 6 meses) e com a media da empresa.
4. Correlacionar: Cruza a alta dos indicadores com eventos de contexto (nova meta, troca de gestor) e com o que a area disse nas pesquisas.
5. Classificar: Associa o padrao a um fator de risco psicossocial (sobrecarga, lideranca, assedio etc.) e da um nivel: verde, amarelo ou vermelho.
6. Gerar o ponto focal: Escreve o card de atencao com evidencias, hipotese e acao sugerida, em linguagem simples.
7. Escalar: Envia ao RH responsavel e para. Nada e registrado como decisao sem aprovacao humana.
8. Registrar: Apos aprovacao, inclui o risco no inventario do PGR e o plano de acao, com responsavel e prazo.
9. Acompanhar: Nos meses seguintes, mede se os indicadores da area melhoraram e reabre o caso se nao melhoraram.

### 3.3 O ponto focal de atencao (o que o RH recebe)
Exemplo do card emitido pelo Pulso:
- ATENCAO ALTA | Area: Atendimento ao Cliente (32 pessoas)
- O que mudou nos ultimos 3 meses: dias de atestado +45%, horas extras +60%, 4 pedidos de demissao (media da empresa: 1), nota de carga de trabalho na pesquisa pulso caiu de 3,9 para 2,4.
- Contexto: a alta comeca 2 semanas depois da nova meta de atendimentos por hora (implantada em agosto).
- Fator de risco provavel: sobrecarga e metas excessivas.
- Acao sugerida: revisar a meta com a lideranca, conversa de escuta com o time mediada pelo RH, incluir o risco no inventario do PGR com reavaliacao em 60 dias.
- Fontes consultadas: ponto, folha, desligamentos, pesquisa pulso de outubro.
- Botoes de Decisao: [ Aprovar e registrar no PGR ] [ Ajustar acao ] [ Descartar com justificativa ]

---

## 4. A experiencia da pessoa colaboradora
A parte humana e o que diferencia o Pulso de um painel de indicadores. O colaborador nao e so fonte de dado: ele participa e ve o resultado.
- Escuta curta e anonima: em vez da pesquisa anual de 80 perguntas, o Pulso faz check-ins de 3 perguntas por chat (WhatsApp ou Slack), uma vez por mes. Comentarios livres sao resumidos por tema, sem identificar quem escreveu.
- Pergunta direcionada: quando um sinal acende numa area, o Pulso pode enviar uma pesquisa curta so para ela, para entender a causa antes de o RH agir.
- Devolutiva ("voce falou, a empresa fez"): quando o RH aprova uma acao, o Pulso redige o comunicado para o time explicando o que vai mudar. E isso que faz as pessoas continuarem respondendo.
- Caminho para ajuda: se um comentario indicar sofrimento grave ou assedio, o Pulso nao analisa: orienta para o canal de denuncia ou o apoio psicologico da empresa e alerta o responsavel.

---

## 5. Como o Pulso cumpre o gerenciamento de riscos da NR-1

| Exigencia do GRO | Como o Pulso atende |
| :--- | :--- |
| Identificar perigos | Detecta padroes por area a partir de dados continuos, nao so da percepcao do gestor. |
| Avaliar o risco | Classifica por nivel (verde, amarelo, vermelho) com base na intensidade e na duracao do sinal. |
| Planejar e executar acoes | Sugere acoes de controle; o RH aprova, define responsavel e prazo. |
| Acompanhar | Remede os indicadores da area depois da acao e reabre o caso se nao houver melhora. |
| Documentar | Gera o registro do inventario de riscos e o plano de acao, com historico auditavel para a fiscalizacao. |

---

## 6. Limites e privacidade (guardrails)
Este e o ponto que os jurados vao testar. Os limites fazem parte do produto, nao sao um aviso de rodape.
- So areas, nunca pessoas. O Pulso nao gera ranking nem analise de individuos. Pedidos como "me mostra os atestados da Carla" sao recusados com explicacao.
- Minimo de 5 pessoas por grupo. Abaixo disso os dados nao aparecem, para ninguem ser identificado por exclusao.
- Sem dado de saude individual. Atestados entram so como contagem. CID e diagnostico nao sao lidos (dado sensivel pela LGPD).
- Decisoes com humanos. O agente prepara, o RH aprova. Desempenho do time e so contexto, nunca avaliacao de pessoas (restricao do Desafio Tako).
- Rastro completo. Cada card mostra quais fontes foram consultadas, o raciocinio e quem aprovou.

---

## 7. Casos de demonstracao (dados sinteticos)

| # | Caso | O que o Pulso faz | Mostra |
| :--- | :--- | :--- | :--- |
| 1 | Area de Financeiro estavel | Analisa e nao gera alerta | Nao e alarmista |
| 2 | Atendimento: nova meta, atestados e horas extras em alta | Gera card vermelho de sobrecarga, sugere acao e registra no PGR apos aprovacao | Caminho feliz completo |
| 3 | Logistica: troca de gestor, seguida de 5 pedidos de demissao | Card amarelo de possivel fator de lideranca e pesquisa direcionada a area | Correlacao com contexto |
| 4 | Vendas: 3 denuncias de assedio em 2 meses | Escala imediatamente para compliance, sem ler o conteudo | Escalonamento sensivel |
| 5 | RH pede "os atestados da Carla" | Recusa e explica o motivo (LGPD, foco em areas) | Guardrail etico |
| 6 | Time de Design com 3 pessoas | Nao exibe os dados para nao identificar ninguem | Anonimizacao (&lt; 5 pessoas) |
| 7 | Atendimento 60 dias depois da acao | Indicadores melhoraram; atualiza o PGR e fecha o ciclo | Acompanhamento e eficacia |

---

## 8. Frente de negocio

| Tema | Definicao |
| :--- | :--- |
| Cliente | Empresas medias e grandes com CLT (a partir de ~100 funcionarios), comecando por setores de alta pressao: atendimento, varejo, saude, logistica. |
| Quem compra | Diretoria de pessoas e juridico. Quem usa: RH, DP e SESMT. |
| Modelo | SaaS por colaborador/mes (hipotese: R$ 4 a R$ 8), ou add-on de suites de RH e folha. |
| Mercado | Toda empresa com empregados CLT precisa cumprir a NR-1. |
| Concorrencia | Consultorias de SST (caras e pontuais), plataformas de pesquisa de clima (sem cruzar dados operacionais) e planilhas. |
| Diferencial | Monitoramento continuo com dados que a empresa ja tem, documentacao pronta para fiscalizacao e anonimizacao por padrao. |
| Encaixe com a Tako | Plataformas de RH e folha ja guardam ponto, afastamentos e desligamentos. O Pulso transforma esses dados em conformidade com a NR-1. |
| Como mostrar o ganho | Horas gastas montando o inventario a mao contra o agente; custo por execucao; tempo entre o sinal aparecer e o RH agir. |

---

## 9. Frente tecnica
- Gatilho: execucao agendada (fechamento de folha) ou pedido do RH no chat ("como esta o time de Logistica?").
- Cerebro: modelo de linguagem por API em laco de ferramentas (Featherless/GLM ou similar).
- Ferramentas (mocks): consultar_ponto, consultar_atestados_agregados, consultar_desligamentos, consultar_denuncias_contagem, consultar_pesquisas, consultar_eventos_org, abrir_card_rh, registrar_pgr, enviar_pesquisa.
- Regras deterministicas + LLM: os calculos de variacao, limites e anonimizacao sao codigo; o LLM correlaciona, explica, classifica o fator e redige card, registro e comunicados.
- Rastro: log de cada passo e tracing com auditoria.
- Medicao: os 7 casos acima como mini conjunto de avaliacao, mais custo por execucao.
- Dados: empresa ficticia com 6 a 8 areas, ~150 funcionarios e 6 meses de historico. Nenhum dado real.

---

## 10. Estrutura do Monorepo (Clean Architecture)

```
converge-challenge-hackton/
|-- .github/
|   `-- workflows/
|       |-- ci.yml                   # Pipeline de Lint (Ruff), Mypy e Testes Unitarios
|       `-- cd.yml                   # Deploy continuo automatizado
|-- .pre-commit-config.yaml          # Hooks do Git: Ruff format, Ruff check, Mypy
|-- backend/                         # Python 3.11+ com FastAPI
|   |-- pyproject.toml               # Configuracoes de ferramentas (Ruff, Mypy, Pytest)
|   |-- requirements.txt             # Dependencias da aplicacao
|   |-- app/
|   |   |-- domain/                  # Entidades puras e contratos de repositorios
|   |   |   |-- entities/            # Area, RiskCard, PsychosocialRiskFactor, Signals, PgrRiskItem, Survey
|   |   |   `-- repositories/        # Interfaces abstratas de persistencia
|   |   |-- application/             # Casos de uso de negocio e DTOs
|   |   |   |-- dtos/                # Schemas de dados (signals, risk_cards, pgr, chat)
|   |   |   `-- use_cases/           # Coleta, Analise NR-1, Card RH, Registro PGR, Acompanhamento, Chat
|   |   |-- infrastructure/          # Adaptadores e ferramentas externas
|   |   |   |-- tools/               # Ferramentas do agente (ponto, folha, atestados, denuncias, pgr)
|   |   |   |-- guardrails/          # Validacao de 5 pessoas e bloqueio de consultas individuais
|   |   |   |-- llm/                 # Agente Pulso em laco de ferramentas (Featherless/GLM)
|   |   |   `-- repositories/        # Repositorios em memoria com os 7 casos sinteticos
|   |   `-- presentation/            # Camada de apresentacao REST
|   |       |-- main.py              # Ponto de entrada FastAPI
|   |       `-- api/v1/endpoints/    # Rotas (areas, risk-cards, pgr, chat, health)
|   |-- scripts/
|   |   `-- seed_synthetic_data.py   # Geracao da empresa ficticia (~150 colaboradores, 7 cenarios)
|   `-- tests/
|       `-- unit/                    # Testes de entidades e guardrails eticos
`-- frontend/                        # Angular 17+ / TypeScript / Tailwind CSS
    |-- package.json                 # Dependencias do Node
    |-- tsconfig.json                # Configuracao do compilador TypeScript
    `-- src/
        |-- app/                     # Rotas e layout base do Next.js
        |-- components/
        |   |-- rh-dashboard/        # RiskFocusCard, PgrInventoryTable, AreaSignalsView, AgentChatConsole
        |   |-- employee-experience/ # MicroSurveyModal, FeedbackDevolutivaCard
        |   `-- common/              # Componentes visuais auxiliares
        |-- services/                # Cliente de integracao com a API
        `-- types/                   # Tipos do dominio (nr1, signals, riskCard)
```

---

## 11. Instrucoes de Execucao Local

### Backend (Python 3.11+)
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Executar linter e checagem de formatacao
ruff check .
ruff format --check .

# Executar verificador estatico de tipos
mypy app scripts

# Executar testes unitarios dos guardrails e entidades
pytest tests/ -v
```

### Frontend (Angular 17+ / Node.js 20+)
```bash
cd frontend
npm install
npm run type-check
npm start
```
