"""Fixtures sinteticas da frente RAG (sem dados pessoais reais)."""

from dataclasses import dataclass, field
from datetime import date
from uuid import UUID

from app.knowledge.domain import CategoriaDocumento, ContextoAutorizado
from app.knowledge.dtos import CadastroTextoRequest
from app.knowledge.grounding import RespondedorFundamentado
from app.knowledge.repository import (
    ArmazenamentoOriginalEmMemoria,
    RepositorioConhecimentoEmMemoria,
)
from app.knowledge.retrieval import RecuperadorTextual
from app.knowledge.service import ServicoConhecimento

EMPRESA_A = UUID("00000000-0000-0000-0000-00000000000a")
EMPRESA_B = UUID("00000000-0000-0000-0000-00000000000b")
USUARIO_RH = UUID("00000000-0000-0000-0000-0000000000f1")

POLITICA_APOIO = """# Canais de apoio

O Programa Escuta oferece apoio psicologico gratuito e confidencial para colaboradores e
dependentes, com atendimento 24 horas pelo telefone 0800 000 0000 e por chat no portal interno.

# Revisao de metas

Quando os indicadores apontarem sobrecarga, a lideranca deve revisar as metas da equipe com o
RH e registrar a medida no plano de acao do PGR.
"""

POLITICA_APOIO_V2 = """# Canais de apoio

O Programa Cuidar substituiu o antigo programa e oferece apoio psicologico gratuito com
agendamento pelo aplicativo de beneficios.
"""


def ctx(
    empresa: UUID = EMPRESA_A, papeis: frozenset[str] = frozenset({"RH"})
) -> ContextoAutorizado:
    return ContextoAutorizado(empresa, USUARIO_RH, papeis, frozenset({"RH"}), "req-teste")


def cadastro(texto: str = POLITICA_APOIO, **extra: object) -> CadastroTextoRequest:
    dados: dict[str, object] = {
        "titulo": "Politica de saude emocional",
        "categoria": CategoriaDocumento.POLITICA,
        "responsavel": "RH Corporativo",
        "texto": texto,
        "vigencia_inicio": date(2026, 1, 1),
        "confirma_sem_dados_sensiveis": True,
    }
    dados.update(extra)
    return CadastroTextoRequest(**dados)  # type: ignore[arg-type]


class GeradorFalso:
    nome_modelo = "falso"

    def __init__(self, resposta: str = "", falhar: bool = False) -> None:
        self.resposta = resposta
        self.falhar = falhar
        self.chamadas: list[tuple[str, str]] = []

    def gerar(self, sistema: str, usuario: str) -> str:
        self.chamadas.append((sistema, usuario))
        if self.falhar:
            raise TimeoutError("featherless lento")
        return self.resposta


@dataclass
class Ambiente:
    repo: RepositorioConhecimentoEmMemoria = field(default_factory=RepositorioConhecimentoEmMemoria)
    armazenamento: ArmazenamentoOriginalEmMemoria = field(
        default_factory=ArmazenamentoOriginalEmMemoria
    )

    def __post_init__(self) -> None:
        self.servico = ServicoConhecimento(self.repo, self.armazenamento)
        self.recuperador = RecuperadorTextual(self.repo)

    def respondedor(self, gerador: object | None = None) -> RespondedorFundamentado:
        return RespondedorFundamentado(self.recuperador, gerador)  # type: ignore[arg-type]
