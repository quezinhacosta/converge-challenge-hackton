"""OCR Vision adapter for parsing medical certificates and doctor notes."""

from typing import Any, Dict


class VisionMedicalCertificateParser:
    """Extracts structured clinical and administrative fields from medical certificates.

    Utilizes Vision APIs / OCR to parse:
        - Doctor name and Regional Medical Council ID (CRM)
        - Issue date and start of leave
        - Total duration in calendar days
        - International Classification of Diseases (CID/ICD code)
        - Document legibility and tampering indicators
    """

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize OCR vision client.

        Args:
            api_key: Optional API key for third-party OCR / Vision endpoint.
        """
        self.api_key = api_key

    def extract_certificate_data(self, file_url: str) -> Dict[str, Any]:
        """Perform OCR and information extraction on medical certificate file.

        Args:
            file_url: URI or local path of the certificate image or PDF.

        Returns:
            Dict[str, Any]: Extracted metadata containing legibility status,
                granted days, doctor details, and validation warnings.
        """
        raise NotImplementedError(
            "VisionMedicalCertificateParser.extract_certificate_data is a structural stub."
        )
