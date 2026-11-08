# Fine-Tuning do Llama-3.1-8B-Instruct (vitAI NR-1 Agent)

Pipeline completo para ajuste fino supervisionado (SFT) do modelo **`meta-llama/Llama-3.1-8B-Instruct`** utilizando **QLoRA (4-bit NF4) + PEFT + TRL**, salvando exclusivamente a **camada de ajustes (LoRA Adapters)**.

---

## 1. Estrutura dos Arquivos

```
ml_training/
├── requirements.txt            # Dependencias PyTorch, Transformers, PEFT, TRL, BitsAndBytes
├── generate_llama_dataset.py   # Gerador de instrucoes no formato ChatML do Llama 3.1
├── train_llama.py              # Script principal de fine-tuning QLoRA (salva em lora_adapters/)
├── run_inference.py            # Teste de inferencia carregando modelo base + LoRA adapter
├── train_dataset.jsonl         # Dataset de treino gerado (1.020 conversas estruturadas)
├── val_dataset.jsonl           # Dataset de validacao gerado (180 conversas estruturadas)
├── lora_adapters/              # Diretorio de saida com a camada de ajustes (criado no treino)
│   ├── adapter_config.json     # Hiperparametros do LoRA (rank, alpha, target modules)
│   └── adapter_model.safetensors # Pesos treinados da camada de ajuste
└── README.md                   # Este guia
```

---

## 2. Passo 1: Acesso ao Modelo no Hugging Face (Gated Model)

O modelo `meta-llama/Llama-3.1-8B-Instruct` exige concordância com os termos de licença da Meta:

1. Acesse: **https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct**
2. Clique em **"Agree and access repository"** (a aprovação costuma ser imediata).
3. Vá em **https://huggingface.co/settings/tokens** e crie um token do tipo `Read`.
4. No terminal da sua máquina, exporte o token:
   ```bash
   export HF_TOKEN="seu_token_aqui"
   ```
   *(Ou execute `huggingface-cli login` e cole o token quando solicitado)*.

---

## 3. Passo 2: Instalação das Dependências

Instale os pacotes com suporte a CUDA e quantização de 4 bits:

```bash
cd ml_training
pip install -r requirements.txt
```

> **Verificação de GPU**: Certifique-se de que `torch.cuda.is_available()` retorna `True` e que sua GPU possui ao menos 12GB de VRAM.

---

## 4. Passo 3: Geração do Dataset de Treinamento

O script gera dados simulando casos reais de conformidade com a NR-1 / Portaria MTE nº 1.419/2024 (Sobrecarga de Trabalho, Conflito de Gestão, Assédio no Canal de Ética, Equipes Estáveis e Proteção LGPD para grupos N < 5):

```bash
python3 generate_llama_dataset.py
```

Isso criará:
- `train_dataset.jsonl` (1.020 conversas)
- `val_dataset.jsonl` (180 conversas)

---

## 5. Passo 4: Executar o Treinamento

Inicie o fine-tuning da camada de ajustes (LoRA):

```bash
python3 train_llama.py
```

### Argumentos Opcionais Customizáveis:
```bash
python3 train_llama.py \
  --epochs 3 \
  --batch_size 2 \
  --grad_accum 4 \
  --lr 2e-4 \
  --lora_r 16 \
  --lora_alpha 32 \
  --output_dir lora_adapters
```

Ao término, a pasta **`lora_adapters/`** conterá a camada de ajustes:
- `adapter_config.json`
- `adapter_model.safetensors`
- `tokenizer_config.json`

---

## 6. Passo 5: Testar a Inferência com os Adaptadores

Para testar a geração do modelo com os adaptadores aplicados sobre os cenários do desafio:

```bash
python3 run_inference.py
```
