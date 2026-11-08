# Fine-Tuning do Mistral-7B-Instruct-v0.3 (vitAI NR-1 Agent)

Pipeline completo para ajuste fino supervisionado (SFT) do modelo **`mistralai/Mistral-7B-Instruct-v0.3`** utilizando **QLoRA (4-bit NF4) + PEFT + TRL**, salvando exclusivamente a **camada de ajustes (LoRA Adapters)**.

Link oficial do modelo: **[https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3)**

---

## 1. Vantagens do Mistral-7B-Instruct-v0.3

- **Licença Aberta Apache 2.0**: Não exige aprovação manual nem termos restritos da Meta. O download é público e imediato.
- **Janela de Contexto de 32k Tokens**: Suporta históricos longos e múltiplos cenários de auditoria.
- **Suporte Nativo a Chamada de Funções e Ferramentas (Function Calling)** via v3 Tokenizer.
- **Excelente Eficiência de VRAM**: Roda com QLoRA 4-bit ocupando em torno de 6 a 8 GB de memória de vídeo, ideal para GPUs como RTX 3060, 3080, 4070, 4080, 4090, A10 ou T4.

---

## 2. Estrutura dos Arquivos

```
ml_training/
├── requirements.txt              # Dependencias PyTorch, Transformers, PEFT, TRL, BitsAndBytes, mistral_common
├── generate_mistral_dataset.py   # Gerador de instrucoes no padrao de chat do Mistral
├── train_mistral.py              # Script principal de fine-tuning QLoRA (salva em lora_adapters/)
├── run_inference.py              # Teste de inferencia carregando modelo base + LoRA adapter
├── train_dataset.jsonl           # 1.020 amostras de treino formatadas em ChatML
├── val_dataset.jsonl             # 180 amostras de validacao formatadas em ChatML
├── lora_adapters/                # Diretorio onde a camada de ajustes sera salva:
│   ├── adapter_config.json       # Hiperparametros do LoRA (rank, alpha, target modules)
│   └── adapter_model.safetensors # Pesos treinados da camada de ajuste
└── README.md                     # Este guia
```

---

## 3. Passo 1: Instalação das Dependências

No seu ambiente Python com suporte a GPU NVIDIA CUDA:

```bash
cd ml_training
pip install -r requirements.txt
```

> **Dica**: Certifique-se de que o PyTorch reconhece a sua GPU:
> ```bash
> python3 -c "import torch; print('CUDA disponivel:', torch.cuda.is_available(), '| GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
> ```

---

## 4. Passo 2: Geração do Dataset de Treinamento

O dataset de 1.200 amostras com os casos da NR-1 / Portaria MTE nº 1.419/2024 (Sobrecarga de Trabalho, Conflito de Gestão, Assédio no Canal de Ética, Equipes Estáveis e Proteção LGPD para grupos N < 5) já foi gerado. Se quiser regenerar:

```bash
python3 generate_mistral_dataset.py
```

Isso gera:
- `train_dataset.jsonl` (1.020 conversas)
- `val_dataset.jsonl` (180 conversas)

---

## 5. Passo 3: Executar o Treinamento da Camada de Ajustes

Execute o script de fine-tuning:

```bash
python3 train_mistral.py
```

### Argumentos Customizáveis (opcional):
```bash
python3 train_mistral.py \
  --base_model mistralai/Mistral-7B-Instruct-v0.3 \
  --epochs 3 \
  --batch_size 2 \
  --grad_accum 4 \
  --lr 2e-4 \
  --lora_r 16 \
  --lora_alpha 32 \
  --output_dir lora_adapters
```

Ao final do treinamento, o script salvará na pasta **`lora_adapters/`**:
- `adapter_config.json`
- `adapter_model.safetensors`
- `tokenizer_config.json`

---

## 6. Passo 4: Testar a Inferência com os Adaptadores

Para testar o modelo treinado com a camada de ajustes acoplada:

```bash
python3 run_inference.py
```
O script carregará o `mistralai/Mistral-7B-Instruct-v0.3`, aplicará os pesos de `lora_adapters/` e executará o diagnóstico nos cenários de demonstração (Atendimento e Logística).
