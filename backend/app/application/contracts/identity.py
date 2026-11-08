"""Identidade confiavel resolvida no servidor, nunca pelo modelo ou pelo body."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ContextoAutorizado:
    empresa_id: UUID
    usuario_id: UUID
    papeis: frozenset[str]
    escopos_permitidos: frozenset[str]
    request_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.papeis, frozenset) or not isinstance(
            self.escopos_permitidos, frozenset
        ):
            raise TypeError("Papeis e escopos devem ser frozenset.")
