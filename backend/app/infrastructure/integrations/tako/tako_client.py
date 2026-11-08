"""Cliente HTTP para a API da Tako (customer-api.8arm.io).

Implementa os endpoints documentados na plataforma da Tako:
- POST /api/v1/auth/token (Autenticação JWT)
- POST /api/v1/organization/contracts (Listagem de contratos por status)
- GET  /api/v1/organization/contracts/ (Detalhes de departamento e liderança)
- GET  /api/v2/contracts/{contractId}/payslips (Holerites e Horas Extras)
- GET  /api/v2/contracts/{contractId}/vacations/{vacationId} (Férias e Afastamentos)
- GET  /api/v1/webhook/public-keys (Chaves públicas para validação de webhooks)
"""

import json
import logging
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_TAKO_BASE_URL = "https://customer-api.8arm.io"


class TakoApiClient:
    """Cliente oficial para interagir com a Customer API da Tako."""

    def __init__(
        self,
        base_url: str | None = None,
        organization_id: str | None = None,
        access_key: str | None = None,
        access_secret: str | None = None,
        timeout_seconds: float = 8.0,
    ) -> None:
        self.base_url = (base_url or os.getenv("TAKO_API_BASE_URL", DEFAULT_TAKO_BASE_URL)).rstrip("/")
        self.organization_id = organization_id or os.getenv("TAKO_ORGANIZATION_ID")
        self.access_key = access_key or os.getenv("TAKO_ACCESS_KEY")
        self.access_secret = access_secret or os.getenv("TAKO_ACCESS_SECRET")
        self.timeout_seconds = timeout_seconds
        self._token: str | None = None

    @property
    def has_credentials(self) -> bool:
        """Indica se as credenciais necessárias da Tako estão configuradas."""
        return bool(self.organization_id and self.access_key and self.access_secret)

    def _make_request(
        self,
        method: str,
        path: str,
        data: dict[str, Any] | None = None,
        requires_auth: bool = True,
    ) -> dict[str, Any]:
        """Executa uma requisição HTTP para a API da Tako com tratamento de erro."""
        url = f"{self.base_url}{path}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "vitAI-NR1-Agent/1.0",
        }

        if requires_auth:
            if not self._token:
                self.authenticate()
            if self._token:
                headers["Authorization"] = f"Bearer {self._token}"

        body_bytes = json.dumps(data).encode("utf-8") if data is not None else None
        req = urllib.request.Request(url, data=body_bytes, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                resp_text = resp.read().decode("utf-8")
                return json.loads(resp_text) if resp_text else {}
        except urllib.error.HTTPError as exc:
            err_body = exc.read().decode("utf-8", errors="ignore")
            logger.warning("Erro HTTP %s ao chamar Tako API em %s: %s", exc.code, path, err_body)
            raise RuntimeError(f"Tako API HTTP {exc.code} em {path}: {err_body}") from exc
        except urllib.error.URLError as exc:
            logger.warning("Falha de conexão com Tako API em %s: %s", path, exc.reason)
            raise ConnectionError(f"Falha de rede ao conectar na Tako API: {exc.reason}") from exc

    def authenticate(self) -> str:
        """POST /api/v1/auth/token

        Autentica a organização junto à Tako e armazena o token JWT.
        """
        if not self.has_credentials:
            raise ValueError("Credenciais da Tako (organizationId, accessKey, accessSecret) não informadas.")

        payload = {
            "organizationId": self.organization_id,
            "accessKey": self.access_key,
            "accessSecret": self.access_secret,
        }
        res = self._make_request("POST", "/api/v1/auth/token", data=payload, requires_auth=False)
        token = res.get("token") or res.get("accessToken") or res.get("jwt")
        if not token:
            raise RuntimeError(f"Resposta de autenticação da Tako não continha token: {res}")
        self._token = token
        return token

    def list_contracts(
        self,
        status: str | None = None,
        page: int = 0,
        size: int = 100,
    ) -> dict[str, Any]:
        """POST /api/v1/organization/contracts

        Lista contratos da organização com filtro de status ('active', 'terminated').
        """
        payload: dict[str, Any] = {
            "pagination": {"page": page, "size": size},
        }
        if status:
            payload["status"] = status

        return self._make_request("POST", "/api/v1/organization/contracts", data=payload)

    def get_contract_details(self, contract_id: str) -> dict[str, Any]:
        """GET /api/v1/organization/contracts/?contractId={contract_id}

        Recupera os detalhes de departamento, cargo, liderança (managerId) e dados do contrato.
        """
        path = f"/api/v1/organization/contracts/?contractId={urllib.parse.quote(contract_id)}"
        return self._make_request("GET", path)

    def get_payslips(self, contract_id: str, period: str) -> list[dict[str, Any]]:
        """GET /api/v2/contracts/{contractId}/payslips?period={period}

        Consulta os itens da folha de pagamento do colaborador na competência informada (ex: '2026-10').
        Utilizado para extrair horas extras e adicionais de sobrejornada.
        """
        path = f"/api/v2/contracts/{urllib.parse.quote(contract_id)}/payslips?period={urllib.parse.quote(period)}"
        res = self._make_request("GET", path)
        if isinstance(res, list):
            return res
        return res.get("items", res.get("data", []))

    def get_vacation_details(self, contract_id: str, vacation_id: str) -> dict[str, Any]:
        """GET /api/v2/contracts/{contractId}/vacations/{vacationId}

        Consulta dados de programação ou gozo de férias do colaborador.
        """
        path = f"/api/v2/contracts/{urllib.parse.quote(contract_id)}/vacations/{urllib.parse.quote(vacation_id)}"
        return self._make_request("GET", path)

    def get_webhook_public_keys(self) -> list[dict[str, Any]]:
        """GET /api/v1/webhook/public-keys

        Recupera as chaves RSA públicas da Tako para validação criptográfica de webhooks.
        """
        res = self._make_request("GET", "/api/v1/webhook/public-keys", requires_auth=False)
        return res if isinstance(res, list) else res.get("keys", [])
