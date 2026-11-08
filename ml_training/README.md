# Modulo de Treinamento de Machine Learning (NR-1 Risk Engine)

Este diretorio contem o pipeline completo para geracao de dataset sintetico, treinamento de modelo supervisionado e inferencia tabular com explicabilidade legal aditiva (SHAP) para governanca de riscos psicossociais segundo a **NR-1** e **Portaria MTE nº 1.419/2024**.

---

## 1. Estrutura do Diretorio

```
ml_training/
├── generate_dataset.py       # Gerador de dados com correlacoes empiricas da NR-1
├── train_model.py            # Treinamento Gradient Boosted Decision Trees + SHAP
├── trained_engine.py         # Motor de inferencia compativel com BaseRiskEngine
├── test_engine.py            # Bateria de testes nos cenarios oficiais
├── dataset_nr1.csv           # Dataset gerado (formato CSV)
├── dataset_nr1.json          # Dataset gerado (formato JSON)
├── artifacts/
│   ├── model_weights.json    # Pesos treinados, thresholds das arvores e baselines
│   └── train_report.json     # Metricas de avaliacao (R2, RMSE, MAE, Acuracia)
└── README.md                 # Este documento
```

---

## 2. Como Gerar o Dataset

O script simula 1.500 amostras corporativas com quatro padroes fundamentais:
1. **Equipes Estaveis (Risco Baixo - Verde)**: baixa variacao de atestados, horas extras sob controle, turnover estavel.
2. **Sobrecarga de Trabalho (Risco Alto/Critico)**: explosao de horas extras (>20%) combinada com atestados medicos (>30%).
3. **Conflito de Lideranca e Clima Degradado**: queda brusca na pesquisa pulso associada a pedidos atipicos de demissao voluntaria.
4. **Denuncias Graves no Canal de Etica / Assedio**: isolamento etico com acionamento de protocolo confidencial fora do PGR.

```bash
cd ml_training
python3 generate_dataset.py
```

---

## 3. Como Treinar o Modelo

O script `train_model.py`:
- Realiza split de 80% treino e 20% teste.
- Treina ensemble aditivo com Gradient Boosting sobre residuos quadraticos.
- Calcula metricas de avaliacao no conjunto de teste independente.
- Salva os artefatos em `artifacts/model_weights.json` e `artifacts/train_report.json`.

```bash
cd ml_training
python3 train_model.py
```

### Metricas Tipicas Obtidas no Teste:
- **R² (Coeficiente de Determinacao)**: `0.96+`
- **MAE (Erro Medio Absoluto)**: `< 5.0 pontos`
- **Acuracia na Classificacao de Severidade**: `94%+`

---

## 4. Como Validar a Inferencia

O script `test_engine.py` avalia a predicao do motor treinado sobre os quatro cenarios do desafio:

```bash
cd ml_training
python3 test_engine.py
```

---

## 5. Como Plugar este Motor no Backend vitAI

No seu script ou inicializacao da aplicacao:

```python
import sys
import os

# Adiciona o diretorio ml_training ao path
sys.path.insert(0, os.path.abspath("ml_training"))

from trained_engine import activate_trained_engine

# Instancia o modelo treinado e o registra como motor ativo no backend
active_engine = activate_trained_engine()
```

A partir desse momento, todas as chamadas de fechamento mensal, consultas de risco e explicabilidade SHAP na API REST e no Dashboard consumirao os artefatos do modelo treinado.
