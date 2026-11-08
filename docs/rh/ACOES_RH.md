# VytAI — execução operacional para o RH

Base: feature/structured-data, fundação 4195e82. Esta entrega não incorpora a branch documental do Claude.

## Entregue

- Portal `/acoes-rh`: preparar intervenção, revisar conteúdo e destinatários, aprovar execução, acompanhar tarefas, registrar evidências e conferir resultados incertos.
- API `/api/v1/rh`: contexto de empresa e usuário exclusivamente da autenticação existente. Papéis RH; nenhuma identidade aceita no body.
- Ferramentas Strands por requisição: `preparar_intervencao`, `consultar_pendencias`, `preparar_comunicacao`, `preparar_reavaliacao`. Ferramentas preparam e consultam; aprovação humana ocorre na API/portal.
- Worker persistente no PostgreSQL: claim com SKIP LOCKED, aprovação vinculada ao conteúdo, tentativas limitadas, leases e ledger de execução. Tarefa e lembretes derivados são gravados na mesma transação da confirmação.
- Adaptadores HTTP para Slack e Google Calendar, desligados por padrão. Texto neutro: não exportar objetivos, documentos, denúncias ou dados de saúde.
- Tarefas exigem evidência declarada pelo RH para concluir. Isso não é uma verificação independente da execução. Reavaliação cria uma tarefa de verificação, sem recalcular score ou registrar melhora.
- Identidade visual baseada no HTML fornecido: violeta, verde-lima, navegação escura, cartões claros e tipografia Inter/Poppins. Nomes: Visão executiva, Fila de deliberação, Ações do RH, Matriz de setores, Inventário PGR, Base de conhecimento e Assistente do RH. Não foram copiados scripts ou métricas fictícias da referência.

## Configuração na nuvem

1. Provisionar PostgreSQL e autenticação da fundação. Executar `alembic upgrade head` com credencial de migração; a revisão nova é `0002_hr_actions`. Runtime usa o papel limitado `vytai_app`. Configurar a sessão autenticada no frontend: esta entrega não implementa uma nova tela de login/OAuth.
2. Criar um principal de serviço com vínculo RH ativo em `empresa_usuario`. Definir `VYTAI_WORKER_EMPRESA_ID` e `VYTAI_WORKER_ACTOR_ID` no servidor. Revogar o vínculo interrompe novos claims.
3. Executar processo dedicado `python -m app.rh_actions.worker` (ou `--once` em um agendamento). Alternativa explícita: `VYTAI_WORKER_ENABLED=true` no Web Service inicia um loop no lifespan. Não usar ambos sem necessidade; concorrência é suportada por claims no banco.
4. O serviço web Free pode dormir. A fila continua no banco, mas pontualidade de lembretes exige processo/agendador sempre ativo. Nenhum serviço pago foi criado nesta entrega.
5. Para envios: `VYTAI_ACTIONS_EXTERNAL_ENABLED=true`, `VYTAI_CONNECTOR_EMPRESA_ID` igual à empresa do worker. MVP usa uma conexão organizacional por deployment, fixada por tenant. Para múltiplas empresas, ainda será necessário um armazenamento seguro de credenciais por tenant e fluxo de instalação OAuth.
6. Slack: bot com `chat:write`, autorizado nos canais de RH. Definir `VYTAI_SLACK_BOT_TOKEN` e `VYTAI_SLACK_ALLOWED_CHANNELS` (IDs separados por vírgula). Não coleta histórico nem mensagens privadas.
7. Agenda: aplicativo Google com acesso Calendar apropriado e consentimento da organização; definir `VYTAI_GOOGLE_CLIENT_ID`, `VYTAI_GOOGLE_CLIENT_SECRET`, `VYTAI_GOOGLE_REFRESH_TOKEN`, `VYTAI_GOOGLE_ALLOWED_CALENDARS`, `VYTAI_GOOGLE_ALLOWED_ATTENDEES`. Convites são explícitos na revisão e limitados aos emails permitidos.
8. Credenciais somente em variáveis secretas do servidor. `.env.example` contém apenas valores vazios. Não configurar essas variáveis no frontend.

## Comportamento e limites

Estados: PENDING → QUEUED → RUNNING → SUCCEEDED; bloqueios usam BLOCKED/FAILED; resultado externo incerto usa UNKNOWN. O RH pode cancelar propostas/ações ainda na fila. Uma operação já em andamento pode ter sido entregue.

A aprovação registra hash do payload, prévia exata e agendamento. Alterações exigem nova revisão. Até três lembretes podem ser autorizados junto com a tarefa, com prévia do texto, canal e datas. Conclusão/cancelamento da tarefa cancela lembretes ainda na fila.

Slack não oferece uma garantia de exactly-once usada por este conector: timeout/5xx ou queda após iniciar envio leva a UNKNOWN, sem reenvio automático. Conferência manual registra autor, justificativa e referência. Agenda usa ID determinístico e verifica a identidade/hash de evento existente antes de inserir novamente. Isso reduz duplicidade, sem prometer garantia absoluta do provedor.

A confirmação de criação de mensagem/evento ou tarefa não significa que a intervenção foi eficaz. Nenhuma ação fecha PGR, decide sobre colaborador ou altera indicadores automaticamente. Jira, respostas interativas por Slack, captura automática de dados Tako e OAuth por organização permanecem fora desta entrega. Não houve envio externo nem validação com credenciais reais.

## Integração com o Claude

Não editar seus módulos RAG. Compartilhados alterados: `presentation/main.py` (router RH e lifespan), `presentation/deps.py` (soma ferramentas operacionais às de áreas e conhecimento), prompt do chat Strands e rotas/shell Angular. Preservar `knowledge.chat_tools` e `KnowledgeIntegration` ao integrar.

DDL novo somente `rh_intervencao`, `rh_acao`, `rh_tarefa`, `rh_evidencia`, `rh_acao_evento`, `rh_tentativa`. Não altera tabelas documentais nem campos compartilhados da fundação. Memória de decisões documental pode consumir o histórico de intervenção com a mesma identidade, sem tratar evidência declarada como fato verificado.

## Validação

Testes PostgreSQL exigem `VYTAI_TEST_DATABASE_URL` apontando para banco descartável exclusivo; fazem migrations e usam RLS com papel sem bypass. Rodar `python -m pytest -q`. Sem essa variável, os testes reais de banco são pulados.

Cobertura operacional: aprovação obrigatória e conteúdo desatualizado, idempotência, tarefa única, concorrência de claims, evidência para conclusão, cancelamento de lembretes, isolamento entre empresas, aprovador revogado, recuperação de lease e resultado Slack incerto. Adaptadores são exercitados por HTTP mock, incluindo confirmação Slack e recuperação de evento Calendar sem segundo insert. Build Angular production e conferência visual desktop/390 px.

Fontes dos adaptadores: https://docs.slack.dev/reference/methods/chat.postMessage/ e https://developers.google.com/workspace/calendar/api/v3/reference/events/insert .
