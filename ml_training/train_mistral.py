"""Script de redirecionamento seguro para train.py.

Evita o download de 14.5 GB do Mistral 7B que causou estouro de disco ('No space left on device')
e executa o pipeline otimizado do train.py.
"""

import sys
from train import main

if __name__ == "__main__":
    print("[vitAI] Redirecionando para o pipeline otimizado train.py (evita estouro de disco de 14.5 GB)...")
    main()

