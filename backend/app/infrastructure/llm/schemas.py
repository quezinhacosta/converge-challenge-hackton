"""Formatos de saida estruturada dos agentes especialistas (validados com Pydantic)."""

from app.application.dtos.compat import BaseModel, Field


class ContextHypothesis(BaseModel):
    """Saida do agente Historiador: hipotese temporal ligando indicadores e eventos."""

    hipotese: str = Field(description="Uma ou duas frases ligando a piora a um evento de contexto.")
    evento_relacionado: str | None = Field(
        default=None, description="Evento de contexto mais provavel, ou null se nao houver."
    )
    confianca: float = Field(ge=0.0, le=1.0, description="Confianca de 0 a 1 na hipotese.")


class RegulatoryAssessment(BaseModel):
    """Saida do agente Regulatorio: enquadramento NR-1 e medida para o plano de acao.

    O fator e o nivel sao decididos em codigo (camada 1); o agente so justifica e propoe a medida.
    """

    justificativa: str = Field(description="Por que esse fator, citando os numeros recebidos.")
    referencia_nr1: str = Field(description="Item da NR-1 que fundamenta o registro.")
    medida_sugerida: str = Field(
        description="Medida organizacional, com responsavel sugerido (papel) e prazo em dias."
    )
    indicador_acompanhamento: str = Field(description="Como medir se a medida funcionou.")
    confianca: float = Field(ge=0.0, le=1.0)


class CardTexts(BaseModel):
    """Saida do agente de Comunicacao para o card do RH."""

    o_que_mudou: str = Field(description="Resumo em linguagem simples do que mudou na area.")
    acao_sugerida: str = Field(description="Acao sugerida em uma ou duas frases.")


class DevolutivaText(BaseModel):
    """Saida do agente de Comunicacao para a devolutiva da equipe."""

    texto: str = Field(description="Mensagem acolhedora 'voce falou, a empresa fez' para a area.")
