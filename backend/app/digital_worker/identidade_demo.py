"""Identidades sinteticas da demonstracao (deterministicas, nao sao segredo nem credencial).

O modo demo so aceita esta empresa: assim, um deploy demo apontado por engano para uma empresa
real nao transforma visitantes anonimos em RH dela.
"""

from uuid import UUID, uuid5

BASE = UUID("5f0c1a2e-7d1b-4f3e-9a51-6d0e7c2b9a10")
EMPRESA_DEMO = uuid5(BASE, "empresa-demo")
USUARIO_DEMO = uuid5(BASE, "rh-demo")
