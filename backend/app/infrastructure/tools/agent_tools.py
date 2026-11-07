"""Ferramentas operacionais (tools) consumidas pelo agente Pulso em seu laco de raciocinio."""

from typing import Any, Dict, List


class PulsoAgentTools:
    """Conjunto de ferramentas (tools) para leitura de sinais de RH e atuacao do agente.

    Regra de Ouro da NR-1 / Guardrail:
        - Todas as ferramentas de consulta operam estritamente por ID de area.
        - Nenhuma ferramenta aceita CPF, nome ou identificador individual de funcionario.
    """

    def consultar_ponto(self, area_id: str, meses: int = 6) -> Dict[str, Any]:
        """Consulta horas extras medias, banco de horas e intervalos nao cumpridos da area.

        Argumentos:
            area_id: Identificador da area.
            meses: Quantidade de meses de historico.
        """
        raise NotImplementedError("consultar_ponto e um stub de ferramenta estrutural.")

    def consultar_atestados_agregados(self, area_id: str, meses: int = 6) -> Dict[str, Any]:
        """Consulta quantidade e dias totais de atestados por mes para a area (sem ler CID nem medico).

        Argumentos:
            area_id: Identificador da area.
            meses: Quantidade de meses de historico.
        """
        raise NotImplementedError("consultar_atestados_agregados e um stub de ferramenta estrutural.")

    def consultar_desligamentos(self, area_id: str, meses: int = 6) -> Dict[str, Any]:
        """Consulta turnover, pedidos de demissao e temas agregados de saida para a area.

        Argumentos:
            area_id: Identificador da area.
            meses: Quantidade de meses de historico.
        """
        raise NotImplementedError("consultar_desligamentos e um stub de ferramenta estrutural.")

    def consultar_denuncias_contagem(self, area_id: str, meses: int = 6) -> Dict[str, Any]:
        """Consulta contagem agregada de denuncias no compliance (sem ler conteudo nem nomes).

        Argumentos:
            area_id: Identificador da area.
            meses: Quantidade de meses de historico.
        """
        raise NotImplementedError("consultar_denuncias_contagem e um stub de ferramenta estrutural.")

    def consultar_pesquisas(self, area_id: str) -> Dict[str, Any]:
        """Consulta notas medias de carga e comentarios sumarizados da pesquisa pulso anonima.

        Argumentos:
            area_id: Identificador da area.
        """
        raise NotImplementedError("consultar_pesquisas e um stub de ferramenta estrutural.")

    def consultar_eventos_org(self, area_id: str) -> List[Dict[str, Any]]:
        """Consulta mudancas de lideranca, novas metas e reestruturacoes associadas a area.

        Argumentos:
            area_id: Identificador da area.
        """
        raise NotImplementedError("consultar_eventos_org e um stub de ferramenta estrutural.")

    def abrir_card_rh(self, card_payload: Dict[str, Any]) -> str:
        """Disponibiliza o card de atencao no painel do RH e aguarda deliberacao humana.

        Argumentos:
            card_payload: Dados estruturados do card (evidencias, hipotese, acao sugerida).
        """
        raise NotImplementedError("abrir_card_rh e um stub de ferramenta estrutural.")

    def registrar_pgr(self, pgr_payload: Dict[str, Any]) -> str:
        """Insere o item de risco no inventario oficial do PGR apos aprovacao humana.

        Argumentos:
            pgr_payload: Dados formais da acao, responsavel e prazo de reavaliacao.
        """
        raise NotImplementedError("registrar_pgr e um stub de ferramenta estrutural.")

    def enviar_pesquisa(self, area_id: str, perguntas: List[str]) -> bool:
        """Dispara micro-pesquisa direcionada aos colaboradores da area via chat (Slack/WhatsApp).

        Argumentos:
            area_id: Identificador da area alvo.
            perguntas: Lista de perguntas curtas de aprofundamento.
        """
        raise NotImplementedError("enviar_pesquisa e um stub de ferramenta estrutural.")
