"""Snapshot validado, imutavel e independente dos DTOs legados de demonstracao."""

from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator


class ImmutableModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", allow_inf_nan=False)


class PeriodoAnalise(ImmutableModel):
    inicio: date
    fim: date
    timezone: str = "America/Fortaleza"

    @model_validator(mode="after")
    def validate_period(self) -> Self:
        from zoneinfo import ZoneInfo

        if self.fim <= self.inicio:
            raise ValueError("fim deve ser posterior a inicio (fim exclusivo).")
        ZoneInfo(self.timezone)
        return self


class FonteIndicador(ImmutableModel):
    evidencia_id: UUID
    fonte: str
    sincronizacao_id: UUID
    periodo: PeriodoAnalise
    extraido_em: datetime


class VariacaoIndicador(ImmutableModel):
    codigo: str
    atual: Decimal | None = None
    baseline: Decimal | None = None
    delta_absoluto: Decimal | None = None
    delta_percentual: Decimal | None = None
    unidade: str
    qualidade: Literal["VALIDO", "SEM_BASELINE", "INCOMPLETO", "INDISPONIVEL"]
    evidencias_ids: tuple[UUID, ...] = ()


class ContribuicaoIndicador(ImmutableModel):
    codigo: str
    regra: str
    pontos: Decimal | None = None
    evidencias_ids: tuple[UUID, ...] = ()


class IndicadoresArea(ImmutableModel):
    snapshot_id: UUID
    empresa_id: UUID
    area_id: str
    periodo: PeriodoAnalise
    calculado_em: datetime
    estado: Literal[
        "ELEGIVEL", "BLOQUEADO_PRIVACIDADE", "DADOS_INSUFICIENTES", "FONTE_INDISPONIVEL"
    ]
    quorum_ok: bool | None
    score: Decimal | None = None
    nivel: Literal["VERDE", "AMARELO", "VERMELHO"] | None = None
    fator: str | None = None
    contribuicoes: tuple[ContribuicaoIndicador, ...] = ()
    variacoes: tuple[VariacaoIndicador, ...] = ()
    fontes: tuple[FonteIndicador, ...] = ()
    limitacoes: tuple[str, ...] = ()
    versao_calculo: str
    origem_dados: Literal["REAL", "DEMONSTRACAO", "MISTA"]

    @model_validator(mode="after")
    def validate_classification(self) -> Self:
        if self.estado != "ELEGIVEL" or self.quorum_ok is not True:
            if any(v is not None for v in (self.score, self.nivel, self.fator)):
                raise ValueError("Sem elegibilidade e quorum nao ha classificacao.")
        if self.score is not None and not Decimal(0) <= self.score <= Decimal(100):
            raise ValueError("score deve estar entre 0 e 100.")
        if self.calculado_em.tzinfo is None:
            raise ValueError("calculado_em deve ter timezone.")
        return self
