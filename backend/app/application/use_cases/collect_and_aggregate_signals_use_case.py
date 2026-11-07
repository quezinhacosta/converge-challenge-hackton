"""Caso de uso para coleta e anonimizacao de sinais operacionais das areas (Etapas 1 e 2 do Pulso)."""

from typing import Protocol

from app.application.dtos.signal_dto import AreaHistoryComparisonDTO
from app.domain.repositories.interfaces import AreaRepository, SignalRepository


class AnonymizationGuardrail(Protocol):
    """Protocolo do guardrail de anonimizacao e conformidade LGPD."""

    def is_group_protected(self, headcount: int) -> bool:
        """Verifica se o grupo atinge o numero minimo de 5 pessoas."""
        ...


class CollectAndAggregateSignalsUseCase:
    """Executa as Etapas 1 e 2 do Ciclo do Pulso:

    Etapa 1 - Coletar:
        Consulta fontes corporativas (ponto, folha, desligamentos, canal de denuncias, pesquisas)
        e agrega tudo por area.
    Etapa 2 - Anonimizar:
        Oculta qualquer grupo com menos de 5 pessoas e descarta sumariamente dados de saude individuais.
    """

    def __init__(
        self,
        area_repository: AreaRepository,
        signal_repository: SignalRepository,
        anonymizer: AnonymizationGuardrail,
    ) -> None:
        """Inicializa o caso de uso com repositorios e guardrails de protecao."""
        self.area_repository = area_repository
        self.signal_repository = signal_repository
        self.anonymizer = anonymizer

    def execute(self, area_id: str) -> AreaHistoryComparisonDTO:
        """Coleta sinais operacionais da area e valida o quorom de anonimizacao.

        Argumentos:
            area_id: Identificador da area a ser analisada.

        Retorna:
            AreaHistoryComparisonDTO: Metricas agregadas ou flag de anonimizacao ativa se < 5 pessoas.

        Lanca:
            ValueError: Se a area solicitada nao existir no cadastro da organizacao.
        """
        area = self.area_repository.get_by_id(area_id)
        if not area:
            raise ValueError(f"Area com identificador '{area_id}' nao encontrada.")

        is_protected = self.anonymizer.is_group_protected(area.headcount)
        events = self.signal_repository.get_context_events(area_id)
        event_descriptions = [
            f"{e.event_date.strftime('%d/%m/%Y')}: {e.description}" for e in events
        ]

        # Se for grupo pequeno (< 5 pessoas), anonimiza por exclusao (Caso 6: Design)
        if not is_protected:
            return AreaHistoryComparisonDTO(
                area_id=area.id,
                area_name=area.name,
                headcount=area.headcount,
                is_anonymized=True,
                variacao_dias_atestado_pct=0.0,
                variacao_horas_extras_pct=0.0,
                pedidos_demissao_periodo=0,
                media_empresa_pedidos_demissao=1.0,
                nota_carga_trabalho_atual=None,
                nota_carga_trabalho_anterior=None,
                eventos_contexto_recentes=event_descriptions,
            )

        metrics_history = self.signal_repository.get_metrics_history(area_id, months=6)
        if not metrics_history:
            return AreaHistoryComparisonDTO(
                area_id=area.id,
                area_name=area.name,
                headcount=area.headcount,
                is_anonymized=False,
                variacao_dias_atestado_pct=0.0,
                variacao_horas_extras_pct=0.0,
                pedidos_demissao_periodo=0,
                media_empresa_pedidos_demissao=1.0,
                nota_carga_trabalho_atual=None,
                nota_carga_trabalho_anterior=None,
                eventos_contexto_recentes=event_descriptions,
            )

        # Metricas da competencia atual (mais recente)
        current_metric = metrics_history[0]

        # Calculo de variacao contra o historico anterior (baseline dos meses anteriores)
        previous_metrics = metrics_history[1:] if len(metrics_history) > 1 else metrics_history
        avg_previous_days = (
            sum(m.certificate_days_count for m in previous_metrics) / len(previous_metrics)
            if previous_metrics
            else current_metric.certificate_days_count
        )
        avg_previous_he = (
            sum(m.overtime_hours_avg for m in previous_metrics) / len(previous_metrics)
            if previous_metrics
            else current_metric.overtime_hours_avg
        )

        variacao_dias = (
            round(
                ((current_metric.certificate_days_count - avg_previous_days) / avg_previous_days)
                * 100,
                1,
            )
            if avg_previous_days > 0
            else 0.0
        )
        variacao_he = (
            round(
                ((current_metric.overtime_hours_avg - avg_previous_he) / avg_previous_he) * 100, 1
            )
            if avg_previous_he > 0
            else 0.0
        )

        # Nota de pesquisa pulso atual vs anterior
        nota_atual = current_metric.pulse_survey_workload_score
        nota_anterior = (
            previous_metrics[0].pulse_survey_workload_score if previous_metrics else None
        )

        return AreaHistoryComparisonDTO(
            area_id=area.id,
            area_name=area.name,
            headcount=area.headcount,
            is_anonymized=False,
            variacao_dias_atestado_pct=variacao_dias,
            variacao_horas_extras_pct=variacao_he,
            pedidos_demissao_periodo=current_metric.resignation_requests_count,
            media_empresa_pedidos_demissao=1.0,
            nota_carga_trabalho_atual=nota_atual,
            nota_carga_trabalho_anterior=nota_anterior,
            eventos_contexto_recentes=event_descriptions,
        )
