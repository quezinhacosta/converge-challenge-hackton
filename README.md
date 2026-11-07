# PAYTRUST (POWERED BY TAKO)

Digital Worker de Governanca, Anti-Fraude e Afastamentos na Folha de Pagamento
Hackathon: Converge Challenge powered by Tako

---

## 1. Resumo Executivo e Tese de Negocio

### Definicao do Produto
O PayTrust e um digital worker e middleware de inteligencia financeira para folha de pagamento corporativa. Ele combina auditoria preditiva anti-fraude via Machine Learning com automacao do ciclo de afastamentos, calculo de diferenca salarial por substituicao temporaria (Sumula 159 do TST) e explicabilidade de holerite em tempo real para colaboradores.

### O Problema de Mercado
Os sistemas de ERP e softwares de Recursos Humanos tradicionais (como TOTVS, Senior e ADP) atuam como "calculadoras cegas": processam lancamentos manuais, cartoes de ponto e aprovacoes de gestores sem analisar o historico comportamental dos colaboradores ou regras trabalhistas dinamicas.

- Passivos Trabalhistas e Erros Ocultos: Inconsistencias em adicionais, calculos imprecisos de afastamento e fraudes em horas extras atingem entre 5% e 8% das folhas de pagamento corporativas.
- Retrabalho Operacional: O Departamento Pessoal (DP) consome dias corrigindo inconsistencias no eSocial e respondendo chamados recorrentes de colaboradores com duvidas sobre os descontos em seus holerites.

### Tese de Negocio e Escala
- Modelo SaaS B2B: Cobranca mensal por vida auditada (R$ 3,00 a R$ 6,00 por colaborador/mes).
- Retorno sobre Investimento (ROI) Imediato: Barrar um unico caso indevido de hora extra ou evitar uma acao trabalhista financia a plataforma por anos.
- Atratividade para M&A: Camada modular de governanca pre-pagamento desenhada para plugar facilmente em grandes suites de ERP e HRTechs do mercado (TOTVS, Senior, ADP, Flash, Caju).

---

## 2. Arquitetura de Inteligencia Artificial em Duas Camadas

O PayTrust opera com uma arquitetura desacoplada em duas camadas de inteligencia:

```
+-----------------------------------------------------------+
|   Entrada: Lote da Folha (CSV/JSON) + Atestados (Img/PDF) |
+-----------------------------+-----------------------------+
                              |
                              v
+-----------------------------------------------------------+
|   CAMADA 1: Predicao e Deteccao de Anomalias (Motor ML)   |
|   - Scikit-Learn (Isolation Forest / LinearSVC)           |
|   - Gera o PayTrust Score continuo (0 a 100)              |
+-----------------------------+-----------------------------+
                              |
                              v
+-----------------------------------------------------------+
|   CAMADA 2: Compliance Generativo e OCR Vision (Motor LLM)|
|   - OCR Vision para extracao estruturada de atestados     |
|   - RAG com legislacao trabalhista (CLT) e Sumula 159 TST |
+-----------------------------+-----------------------------+
                              |
                              v
+-----------------------------------------------------------+
|   Interfaces: Dashboard do DP + Portal do Colaborador     |
+-----------------------------------------------------------+
```

### Matriz das Camadas de IA

| Camada | Tecnologia | Funcao no Produto |
| :--- | :--- | :--- |
| Camada 1: Preditiva e Deteccao (ML) | Scikit-Learn (Isolation Forest / LinearSVC) em Python | Avalia o lote da folha e gera o PayTrust Score (0-100) para identificar anomalias estatisticas, picos incomuns de horas extras e duplicidades. |
| Camada 2: Leitura e Compliance (LLM) | Groq / OpenAI (Llama-3 / GPT-4o-mini) + Vision OCR | Realiza a leitura de atestados medicos, valida o teto de 15 dias da empresa vs. INSS, aplica as regras da Sumula 159 do TST e gera justificativas humanizadas. |

---

## 3. Estrutura do Repositorio (Clean Architecture)

```
converge-challenge-hackton/
|-- .github/
|   `-- workflows/
|       |-- ci.yml                   # Pipeline de Lint (Ruff), Tipagem (Mypy) e Testes do Modelo
|       `-- cd.yml                   # Deploy continuo automatizado do MVP
|-- .pre-commit-config.yaml          # Hooks do Git: Ruff format, Ruff check, Mypy e higiene de arquivos
|-- backend/                         # Python 3.11+ com FastAPI
|   |-- pyproject.toml               # Configuracoes de ferramentas (Ruff, Mypy, Pytest)
|   |-- requirements.txt             # Dependencias de producao e desenvolvimento
|   |-- app/
|   |   |-- domain/                  # Entidades de dominio puras e contratos de repositorios
|   |   |   |-- entities/            # Employee, Absence, Paystub, Anomaly
|   |   |   `-- repositories/        # Interfaces abstratas de persistencia
|   |   |-- application/             # Casos de uso de negocio e Data Transfer Objects (DTOs)
|   |   |   |-- dtos/                # Schemas de requisicao e resposta
|   |   |   `-- use_cases/           # AuditPayrollUseCase, ProcessAbsenceUseCase, CalculateSubstitutionUseCase
|   |   |-- infrastructure/          # Adaptadores e integracoes com servicos externos
|   |   |   |-- ml/                  # Modelo Isolation Forest e artefato compilado (.pkl)
|   |   |   |-- ocr/                 # Adaptador de parser OCR Vision para documentos
|   |   |   |-- llm/                 # Agente de compliance e explicabilidade via LLM
|   |   |   `-- repositories/        # Implementacoes em memoria e adaptadores de banco de dados
|   |   `-- presentation/            # Camada de exposicao HTTP e WebSockets
|   |       |-- main.py              # Fabrica e ponto de entrada da aplicacao FastAPI
|   |       `-- api/v1/endpoints/    # Endpoints REST (health, payroll, absences)
|   |-- scripts/
|   |   `-- train_anomaly_model.py   # Script isolado para treino e serializacao do modelo ML
|   `-- tests/
|       `-- unit/                    # Testes unitarios de entidades de dominio e pipeline de ML
`-- frontend/                        # Next.js / TypeScript / Tailwind CSS
    |-- package.json                 # Configuracao de dependencias do Node
    |-- tsconfig.json                # Configuracao do compilador TypeScript
    `-- src/
        |-- app/                     # Rotas e layout base do Next.js App Router
        |-- components/
        |   |-- dp-dashboard/        # Interface do Analista de DP (AuditActionCenter, AbsenceManager, AnomalyAlertsList)
        |   |-- employee-portal/     # Interface do Colaborador (InteractivePaystub, CertificateUploadModal, ExplainabilityChat)
        |   `-- common/              # Componentes visuais compartilhados (MetricsCard)
        |-- services/                # Clientes de integracao com a API FastAPI
        `-- types/                   # Tipos e interfaces TypeScript do dominio
```

---

## 4. Matriz de Casos de Uso para Demonstracao (MVP)

| Numero | Caso de Uso | Acao Automatica do PayTrust | Impacto / Resultado |
| :--- | :--- | :--- | :--- |
| 1 | Atestado medico simples (3 dias) | OCR extrai dados e lanca os dias abonados sob responsabilidade integral da empresa conforme CLT Art. 476. | Caminho Feliz: Processamento automatico com aviso ao gestor imediato. |
| 2 | Atestado longo (20 dias) | Divide o periodo: 15 dias pagos pela empresa e 5 dias direcionados ao INSS com instrucoes para agendamento de pericia. | Regra de Negocio: Aplicacao do marco legal sem necessidade de divisao manual. |
| 3 | Atestado com imagem ilegivel | Rejeicao imediata no momento do upload com notificacao ao colaborador para reenvio de foto nitida. | Tratamento de Excecao: Bloqueia a entrada de documentos corrompidos ou ilegiveis no DP. |
| 4 | Afastamento sobreposto a ferias | Identifica conflito de datas entre o atestado e ferias agendadas, gerando card de resolucao proativa para o RH. | Escalonamento: Prevencao de choque de beneficios e inconsistencias cadastrais. |
| 5 | Substituicao temporaria (Sumula 159 TST) | Valida carater nao-eventual da substituicao e calcula a Diferenca Salarial Proporcional a ser creditada na folha. | Impacto Financeiro: Conformidade estrita com a jurisprudencia trabalhista. |
| 6 | Anomalia de horas extras (Pico atipico) | Isolation Forest detecta aumento desproporcional (Score 94/100) e retem o pagamento preventivamente para auditoria. | Anti-Fraude: Estancamento de sangramento financeiro antes do pagamento. |

---

## 5. Governanca e Guardrails (Human-in-the-Loop)

Para assegurar conformidade juridica, etica e responsabilidade nas decisoes:

- Papel do Assistente Digital (IA): O agente digital executa a leitura OCR, calcula valores proporcionais de substituicao, infere scores de risco preditivo e redige justificativas referenciando a legislacao.
- Autoridade Humana Exclusiva: O analista de DP ou gestor de RH permanece como a unica autoridade competente para autorizar a liberacao do pagamento ou descartar apontamentos por meio de aprovacao em 1 clique.

---

## 6. Qualidade de Codigo, Ferramentas e CI/CD

### Analise Estatica e Padronizacao
- Ruff: Linter e formatador de codigo Python configurado para o padrao py311.
- Mypy: Checagem estatica estrita de tipagem no dominio, aplicacao e infraestrutura.
- Pre-commit: Hooks locais que garantem validacao sintatica, remocao de espacos em branco e formatacao antes de cada commit.

### Pipeline de CI/CD (GitHub Actions)
- Integracao Continua (`.github/workflows/ci.yml`):
  1. Executa validacao de formatacao e estilo com `ruff check` e `ruff format --check`.
  2. Executa verificacao estatica de tipos com `mypy app scripts`.
  3. Treina e valida o artefato do modelo Isolation Forest e roda a suite `pytest`.
  4. Valida a integridade da configuracao e estrutura do frontend.
- Entrega Continua (`.github/workflows/cd.yml`):
  Prepara o fluxo de deploy automatizado da API FastAPI e da interface web.

---

## 7. Instrucoes de Execucao Local

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

# Treinar artefato do modelo de deteccao de anomalias
python scripts/train_anomaly_model.py

# Executar testes unitarios
pytest tests/ -v
```

### Configuracao do Pre-commit
```bash
pre-commit install
pre-commit run --all-files
```

### Frontend (Node.js 20+)
```bash
cd frontend
npm install
npm run type-check
npm run dev
```
