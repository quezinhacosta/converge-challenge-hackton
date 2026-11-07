#!/usr/bin/env bash
# ==============================================================================
# Script de Execucao do Pulso - Digital Worker NR-1 (Converge Challenge)
# Time Booleanas - Desafio Tako
# ==============================================================================

set -e

echo "=== Iniciando Verificacao e Execucao do Projeto Pulso ==="

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

# 1. Execucao dos Testes Automatizados do Backend (XGBoost, SHAP, Failover, Circuit Breaker)
echo "[1/3] Executando testes unitarios do backend (15 testes cobrindo ML, Resiliencia e os 7 cenarios)..."
cd "$BACKEND_DIR"
python3 -m pytest tests/unit/
python3 -m mypy app scripts

# 2. Verificacao de Build do Frontend Angular
echo "[2/3] Verificando compilacao do frontend Angular (Standalone + Tailwind)..."
cd "$FRONTEND_DIR"
CI=true NG_CLI_ANALYTICS=false npx ng build --configuration production

echo "[3/3] Build verificado com sucesso!"
echo ""
echo "Instrucoes para subir os servidores locais:"
echo "------------------------------------------------------------"
echo "Opcao A: Via Docker Compose (Recomendado):"
echo "  docker compose up --build"
echo ""
echo "Opcao B: Execucao Manual:"
echo "  Terminal 1 (Backend FastAPI):"
echo "    cd backend && uvicorn app.presentation.main:app --reload --port 8000"
echo ""
echo "  Terminal 2 (Frontend Angular):"
echo "    cd frontend && CI=true NG_CLI_ANALYTICS=false npx ng serve --port 4200"
echo ""
echo "Acesse a interface no navegador: http://localhost:4200"
echo "Documentacao da API: http://localhost:8000/docs"
echo "Roteiro do Pitch de 3 minutos: PITCH_ROTEIRO.md"
echo "------------------------------------------------------------"
