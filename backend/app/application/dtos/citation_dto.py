"""Referencias documentais: IDs estaveis e ref vinculada a execucao recuperada."""

from uuid import UUID

from pydantic import Field

from app.application.dtos.compat import ApiModel


class CitacaoDTO(ApiModel):
    ref: str = Field(pattern=r"^C[1-9][0-9]*$")
    documento_id: UUID
    versao_id: UUID
    trecho_id: UUID
    titulo: str
    versao_rotulo: str
    pagina: int | None = Field(default=None, ge=1)
    secao: str | None = None
    trecho: str = Field(default="", max_length=500)
