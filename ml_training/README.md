# Fine-Tuning e Inferencia LoRA (vitAI NR-1 Agent)

Este pipeline treina e integra a camada de adaptadores LoRA especializada na Norma Regulamentadora nº 1 (NR-1) e Portaria MTE nº 1.419/2024 para gestao e governanca de riscos psicossociais.

---

## 1. Modelo Treinado: Mistral-7B-Instruct-v0.3 + LoRA

A camada de adaptadores LoRA foi treinada com sucesso via Google Colab (GPU NVIDIA Tesla T4) e esta integrada ao projeto em:
- `lora_adapters/adapter_config.json` (Modelo Base: `mistralai/Mistral-7B-Instruct-v0.3`, Rank: 16, Alpha: 32)
- `lora_adapters/adapter_model.safetensors` (~83.9 MB)
- `lora_adapters/tokenizer.json`

---

## 2. Integracao com o Backend vitAI

A camada LoRA do Mistral-7B foi integrada diretamente a arquitetura de IA em cascata (FailoverManager):
1. **`MistralLoraProvider`** (`backend/app/infrastructure/llm/resilience/mistral_lora_provider.py`):
   - Provedor on-premise/local de alta fidelidade regulatoria.
   - Gera pareceres tecnicos de riscos psicossociais, hipoteses contextuais e acoes para o PGR.
   - Atende consultas no chat de RH com respeito a privacidade (LGPD).
2. **`FailoverManager`**:
   - Cadeia: Cloud (Strands/Gemini) -> **Mistral 7B LoRA (Local Especializado)** -> Regras Deterministicas.
   - Garante zero indisponibilidade operacional.

---

## 3. Como Testar a Inferencia

Na pasta `ml_training`:

```bash
python3 run_inference.py
```

O script detecta automaticamente a presenca dos adaptadores LoRA e do modelo Mistral 7B, executando os diagnosticos dos cenarios oficiais (Atendimento ao Cliente e Logistica). Em ambiente sem GPU dedicada, o script opera em modo protegido para evitar estouro de memoria RAM.
