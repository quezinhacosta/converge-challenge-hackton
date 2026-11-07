# Pulso como servidor MCP

O Pulso expõe o digital worker como ferramentas MCP. Qualquer agente compatível
(Claude Desktop, MCP Inspector, o agente Otto da Tako, Copilot...) pode usar o Pulso
sem tela própria. O servidor MCP chama a API REST, então o que um agente faz por aqui
aparece no painel web e no Slack.

## Ferramentas

| Ferramenta | O que faz |
|---|---|
| `listar_areas` | Áreas, número de pessoas e se os dados estão ocultos (LGPD) |
| `status_area(area)` | Indicadores agregados de uma área (aceita id ou nome) |
| `analisar_area(area)` | Roda o ciclo do Pulso e abre card se amarelo/vermelho (sem duplicar) |
| `rodar_fechamento()` | Analisa todas as áreas (gatilho do fechamento da folha) |
| `listar_cards_abertos()` | Cards aguardando decisão do RH |
| `decidir_card(...)` | Registra a decisão **humana** do RH (exige `confirmado_pelo_rh=true`) |
| `inventario_pgr()` | Inventário e plano de ação do PGR com rastro de auditoria |
| `perguntar_ao_pulso(pergunta)` | Chat sobre áreas; pedidos sobre pessoas são recusados |

## Como rodar

1. Suba a API (pasta `backend`):
   ```bash
   uvicorn app.presentation.main:app --port 8000
   ```
2. Em outra janela, suba o servidor MCP:
   ```bash
   python -m app.presentation.mcp_server          # stdio
   python -m app.presentation.mcp_server --http   # http://127.0.0.1:8765/mcp
   ```
   `PULSO_API_URL` muda o endereço da API (padrão `http://localhost:8000/api/v1`).

## Claude Desktop

Em `claude_desktop_config.json` (ajuste os caminhos):

```json
{
  "mcpServers": {
    "pulso": {
      "command": "C:\\caminho\\para\\.venv\\Scripts\\python.exe",
      "args": ["-m", "app.presentation.mcp_server"],
      "cwd": "C:\\caminho\\para\\pulso\\backend"
    }
  }
}
```

Exemplo de conversa: "Rode o fechamento do Pulso e me mostre os cards abertos" →
"Aprove o card do Atendimento no PGR, responsável Juliana" (o agente pede sua confirmação
antes de chamar `decidir_card`).

## MCP Inspector

```bash
npx @modelcontextprotocol/inspector python -m app.presentation.mcp_server
```

## Demo sem sustos

- `PULSO_LLM_DEMO_CACHE=.llm_demo_cache.json` grava a primeira resposta boa da IA por área
  e reaproveita nas próximas (rode o fechamento uma vez antes da apresentação).
- `PULSO_LLM_BUDGET=40`: se a IA passar desse tempo, o motor determinístico responde na hora.
