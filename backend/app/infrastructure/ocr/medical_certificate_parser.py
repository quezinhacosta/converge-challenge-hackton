"""Adaptador de OCR Vision para leitura e parsing estruturado de atestados medicos."""

from typing import Any, Dict


class VisionMedicalCertificateParser:
    """Extrai campos clinicos e cadastrais a partir de imagens ou PDFs de atestados medicos.

    Responsabilidades da extracao:
        - Nome do medico assistente e inscricao no CRM.
        - Data de emissao e data de inicio do repouso.
        - Duracao total do afastamento em dias corridos.
        - Codigo CID (Classificacao Internacional de Doencas), quando expresso.
        - Metricas de legibilidade da imagem e indicios visuais de adulteracao.
    """

    def __init__(self, api_key: str | None = None) -> None:
        """Inicializa o cliente do servico de OCR Vision.

        Argumentos:
            api_key: Chave de API opcional para servicos de visao computacional externos.
        """
        self.api_key = api_key

    def extract_certificate_data(self, file_url: str) -> Dict[str, Any]:
        """Executa OCR e extracao de informacoes no arquivo do atestado.

        Argumentos:
            file_url: URI ou caminho local do documento de atestado.

        Retorna:
            Dict[str, Any]: Dicionario com os campos estruturados e status de legibilidade.
        """
        raise NotImplementedError(
            "VisionMedicalCertificateParser.extract_certificate_data e um stub estrutural."
        )
