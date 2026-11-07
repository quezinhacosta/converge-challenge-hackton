"""Entidade de dominio representando uma area ou departamento da organizacao."""

from dataclasses import dataclass


@dataclass
class Area:
    """Representa um time ou departamento sob gestao de riscos psicossociais da NR-1.

    Regra de Anonimizacao (Guardrail NR-1):
        - Grupos com menos de 5 pessoas (headcount < 5) tem seus dados operacionais ocultados
          pelo Pulso para impedir identificacao de individuos por exclusao.

    Atributos:
        id: Identificador unico da area ou setor.
        name: Nome do setor (ex.: Atendimento ao Cliente, Logistica, Vendas).
        headcount: Quantidade total de colaboradores ativos alocados na area.
        manager_name: Nome da lideranca imediata do setor.
        is_active: Indicador se o setor esta em operacao.
        description: Breve descricao das atividades operacionais da equipe.
    """

    id: str
    name: str
    headcount: int
    manager_name: str
    is_active: bool = True
    description: str | None = None

    @property
    def is_eligible_for_analytics(self) -> bool:
        """Indica se a area atinge o quorom minimo de 5 pessoas para exibicao de metricas."""
        return self.headcount >= 5
