# Fine-Tuning Eficiente (vitAI NR-1 Agent)

Este pipeline foi otimizado para executar um treinamento **rápido (20 a 40 minutos)**, com **download leve (~900MB)**, adaptado tanto para **CPU (AMD Ryzen)** quanto para **GPU (NVIDIA CUDA)**, salvando a **camada de ajustes (LoRA Adapters)**.

---

## 1. Por que o Mistral 7B / Llama 8B falhou?

Modelos de 7B a 8B possuem mais de **14,5 GB de arquivos** e exigem:
- Pelo menos **16 GB a 24 GB de memória RAM** só para descompactar os pesos.
- Uma **GPU dedicada NVIDIA com CUDA** para quantização 4-bit (`bitsandbytes`).

No notebook **Acer Aspire A515-45 (AMD Ryzen 5 com 7,1 GB de RAM total)**:
- O download de 14,5 GB esgota o buffer de memória (`RuntimeError: Background writer channel closed`).
- Em CPU pura, treinar 7 bilhões de parâmetros demoraria mais de 15 horas.

---

## 2. A Solução: Small Language Model de Alta Precisão (SLM)

Utilizamos o **`Qwen/Qwen2.5-0.5B-Instruct`** (ou `Qwen2.5-1.5B-Instruct`):
- **Download Leve**: apenas **~900 MB** (baixa em menos de 1 minuto).
- **Consumo de RAM**: cerca de **1,8 GB** (roda com muita folga nos 3,7 GB livres).
- **Tempo de Treinamento**: **20 a 35 minutos** utilizando todos os núcleos do AMD Ryzen 5.
- **Camada de Ajustes LoRA**: salva exatamente em `lora_adapters/adapter_model.safetensors` e `adapter_config.json`.
- **Qualidade**: Modelo de última geração treinado em 18T tokens, com suporte de ponta a português e geração estrita de JSON para conformidade com a NR-1.

---

## 3. Como Executar o Treinamento

No seu ambiente virtual (`.venv`):

```bash
cd ml_training
python3 train.py
```

### O que o script faz:
1. Detecta automaticamente sua CPU (AMD Ryzen 5 com 6 núcleos) ou GPU se disponível.
2. Faz o download rápido de apenas ~900 MB do modelo base.
3. Injeta a camada de adaptadores LoRA (`q_proj`, `v_proj`, `k_proj`, `o_proj`).
4. Treina sobre o dataset da NR-1 / Portaria MTE nº 1.419/2024.
5. Salva a camada de ajustes em:
   - `lora_adapters/adapter_config.json`
   - `lora_adapters/adapter_model.safetensors`

---

## 4. Como Testar a Inferência com os Adaptadores

Após a conclusão do treino:

```bash
python3 run_inference.py
```

O script carregará o modelo base com a sua camada de ajustes LoRA acoplada e gerará os pareceres estruturados para os cenários oficiais do projeto.
