"""Prepara a empresa ficticia de demonstracao no PostgreSQL (dados 100% sinteticos).

    python -m app.digital_worker.demo

Usa DATABASE_URL com credencial de migracao (cria empresa e vinculo RH). Idempotente: rodar de
novo reaproveita a empresa e ignora documentos ja cadastrados. Ao final, imprime as variaveis
para o modo demo (VYTAI_MODE=demo + VYTAI_DEMO_EMPRESA_ID + VYTAI_DEMO_USUARIO_ID).
"""

import os
from datetime import date

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session

from app.application.contracts.identity import ContextoAutorizado
from app.digital_worker.identidade_demo import EMPRESA_DEMO, USUARIO_DEMO
from app.infrastructure.persistence.repositories import RepositoryBundle
from app.knowledge.domain import CategoriaDocumento, ErroConhecimento
from app.knowledge.dtos import CadastroTextoRequest
from app.knowledge.integration import criar_servicos_documentais
from app.presentation.deps import PulsoAppContainer

DOCUMENTOS = [
    (
        "Programa Cuidar - Apoio Psicologico",
        CategoriaDocumento.PROGRAMA_BENEFICIO,
        """# Programa Cuidar

Atendimento psicologico gratuito e confidencial para colaboradores e dependentes, com ate oito
sessoes por ano. O agendamento e feito pelo aplicativo de beneficios, sem passar pelo gestor.
Indicado em casos de sobrecarga, ansiedade e conflitos no trabalho.
""",
    ),
    (
        "Canal de Escuta Anonima",
        CategoriaDocumento.CANAL_APOIO,
        """# Canal de Escuta Anonima

Qualquer colaborador pode relatar sobrecarga, conflito com a lideranca ou desrespeito pelo canal
anonimo do portal interno. A ouvidoria responde em ate dez dias uteis e nunca pede identificacao.
Relatos sobre a lideranca direta sao tratados por um comite fora da area.
""",
    ),
    (
        "Procedimento de Revisao de Metas",
        CategoriaDocumento.PROCEDIMENTO_ACOLHIMENTO,
        """# Revisao de metas

Quando os indicadores apontarem sobrecarga, a lideranca revisa as metas da equipe com o RH em
ate quinze dias e registra a medida no plano de acao do PGR. Pausas de dez minutos apos
atendimentos dificeis sao garantidas no Atendimento ao Cliente.
""",
    ),
    (
        "Plano de Acao Logistica 2025",
        CategoriaDocumento.PLANO_ACAO_ANTERIOR,
        """# Plano de acao da Logistica (2025)

Diante do aumento de horas extras no turno da noite, a empresa revisou a escala e criou pausas
de quinze minutos a cada duas horas. A revisao de escala reduziu a sobrecarga relatada no ciclo
seguinte; a troca de supervisores nao teve efeito perceptivel.
""",
    ),
    (
        "Politica de Saude Emocional",
        CategoriaDocumento.POLITICA,
        """# Politica de saude emocional

A empresa trata riscos psicossociais como parte do gerenciamento de riscos ocupacionais. Metas,
jornadas e relacoes de trabalho sao revistas sempre que os sinais agregados indicarem risco, sem
avaliar pessoas individualmente e sem diagnostico de saude.
""",
    ),
    (
        "Procedimento de Jornada, Pausas e Banco de Horas",
        CategoriaDocumento.PROCEDIMENTO_ACOLHIMENTO,
        """# Jornada, pausas e descanso

Quando as horas extras de uma equipe passam de dez horas por pessoa no mês, o RH e a liderança
revisam a jornada e a escala em até quinze dias. A pausa de quinze minutos a cada duas horas é
garantida, e o descanso entre jornadas nunca é menor que onze horas.

# Banco de horas

O banco de horas é compensado em até seis meses, com folga combinada com a pessoa. Saldo alto de
banco de horas por três meses seguidos abre uma revisão da carga da área.
""",
    ),
    (
        "Programa Liderar com Escuta",
        CategoriaDocumento.PROGRAMA_BENEFICIO,
        """# Programa Liderar com Escuta

Formação para cada gestor nos primeiros noventa dias no cargo: feedback contínuo, conversas de
alinhamento e mediação de conflitos. Quando há conflito entre liderança e equipe, o RH oferece
mediação com um facilitador de fora da área, sem expor quem relatou o problema.
""",
    ),
    (
        "Procedimento de Clareza de Papéis e Responsabilidades",
        CategoriaDocumento.PROCEDIMENTO_ACOLHIMENTO,
        """# Clareza de papel

Cada área mantém um quadro de papel e responsabilidade de cada função, revisado a cada semestre
ou quando houver mudança de atribuição. Toda nova atribuição é combinada por escrito entre a
pessoa e o gestor, com prazo e critério de entrega.
""",
    ),
    (
        "Programa Autonomia no Dia a Dia",
        CategoriaDocumento.PROGRAMA_BENEFICIO,
        """# Autonomia e flexibilidade

As equipes definem com a liderança como organizar o próprio trabalho dentro das metas da área.
Cada pessoa tem autonomia de decisão sobre a ordem das tarefas e flexibilidade de horário de
entrada e saída de até uma hora, combinada com a equipe.
""",
    ),
    (
        "Procedimento de Comunicação em Mudanças",
        CategoriaDocumento.PROCEDIMENTO_ACOLHIMENTO,
        """# Comunicação em mudanças e reestruturação

Toda mudança de estrutura, gestor ou meta é comunicada à equipe antes de entrar em vigor, com o
motivo e o que muda para cada função. Em uma reestruturação, o RH conduz um período de transição
de pelo menos trinta dias, com encontros de dúvidas e canal aberto para preocupações.
""",
    ),
    (
        "Política de Organização do Trabalho e Liderança",
        CategoriaDocumento.POLITICA,
        """# Jornada e horas extras

Horas extras são exceção, não rotina. A jornada é acompanhada por área, e a pausa e o descanso
previstos em lei são respeitados por toda liderança.

# Liderança e conflito

Todo gestor dá feedback regular à equipe. Conflito entre liderança e equipe é tratado com
mediação do RH, nunca com retaliação.

# Papel e responsabilidade

Cada função tem papel e responsabilidade definidos por escrito, e nenhuma atribuição nova é
cobrada sem ter sido combinada.

# Autonomia e decisão

A empresa valoriza a autonomia das equipes: a decisão sobre como organizar o trabalho é tomada
junto com quem faz o trabalho, com flexibilidade sempre que a operação permitir.

# Mudança e comunicação

Toda mudança ou reestruturação tem comunicação prévia e um período de transição acompanhado
pelo RH.
""",
    ),
    (
        "Política de Prevenção ao Assédio",
        CategoriaDocumento.POLITICA,
        """# Prevenção ao assédio

A empresa não tolera assédio moral ou sexual. Toda denúncia pode ser feita pelo canal de ética
do compliance, inclusive de forma anônima, e é apurada por um comitê independente. Retaliação
contra quem denuncia é falta grave.
""",
    ),
]


def engine_administrativo() -> Engine:
    """Conexao de migracao (cria empresa/vinculo). Nao usar no runtime da API."""
    url = os.getenv("DATABASE_URL", "")
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    if not url.startswith("postgresql+psycopg://"):
        raise SystemExit("Configure DATABASE_URL (credencial de migracao).")
    return create_engine(url, hide_parameters=True)


def preparar_demo(engine: Engine) -> dict[str, object]:
    ctx = ContextoAutorizado(
        EMPRESA_DEMO, USUARIO_DEMO, frozenset({"RH"}), frozenset({"RH"}), "demo-bootstrap"
    )
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO empresa(id,nome) VALUES(:id,'Empresa Demonstração (fictícia)') "
                "ON CONFLICT (id) DO UPDATE SET nome=EXCLUDED.nome"
            ),
            {"id": EMPRESA_DEMO},
        )
        conn.execute(
            text(
                "INSERT INTO empresa_usuario(empresa_id,usuario_id,papeis,ativo) "
                "VALUES(:e,:u,ARRAY['RH'],true) ON CONFLICT (empresa_id,usuario_id) "
                "DO UPDATE SET papeis=ARRAY['RH'], ativo=true"
            ),
            {"e": EMPRESA_DEMO, "u": USUARIO_DEMO},
        )
    novos = 0
    with Session(engine) as session, session.begin():
        session.execute(text("SET LOCAL ROLE vytai_app"))
        session.execute(
            text("SELECT set_config('vytai.empresa_id', :empresa, true)"),
            {"empresa": str(EMPRESA_DEMO)},
        )
        bundle = RepositoryBundle(session, EMPRESA_DEMO)
        semear = not bundle.area_repo.list_all()
        PulsoAppContainer(bundle, seed=semear, context=ctx, session=session)
        conhecimento = criar_servicos_documentais(ctx, session)
        for titulo, categoria, texto in DOCUMENTOS:
            try:
                doc = conhecimento.servico.cadastrar_texto(
                    ctx,
                    CadastroTextoRequest(
                        titulo=titulo,
                        categoria=categoria,
                        responsavel="RH Corporativo (demo)",
                        texto=texto,
                        vigencia_inicio=date(2026, 1, 1),
                        confirma_sem_dados_sensiveis=True,
                    ),
                )
                conhecimento.servico.publicar(ctx, doc.versoes[-1].id)
                novos += 1
            except ErroConhecimento as erro:
                if erro.codigo != "DUPLICADO":
                    raise
    return {"empresa": EMPRESA_DEMO, "usuario": USUARIO_DEMO, "semeado": semear, "novos": novos}


def main() -> int:
    r = preparar_demo(engine_administrativo())
    print(
        f"Areas sinteticas: {'semeadas' if r['semeado'] else 'ja existiam'}; "
        f"documentos novos: {r['novos']}"
    )
    print("Configure no backend (somente demonstracao):")
    print("VYTAI_MODE=demo")
    print(f"VYTAI_DEMO_EMPRESA_ID={EMPRESA_DEMO}")
    print(f"VYTAI_DEMO_USUARIO_ID={USUARIO_DEMO}")
    print("Para o ciclo agendado, use os mesmos valores em VYTAI_WORKER_EMPRESA_ID/ACTOR_ID.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
