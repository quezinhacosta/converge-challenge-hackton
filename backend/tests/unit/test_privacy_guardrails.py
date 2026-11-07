"""Testes unitarios dos guardrails eticos e de privacidade do Pulso."""

from app.infrastructure.guardrails.privacy_guardrail import PrivacyAndEthicsGuardrail


def test_minimum_group_size_guardrail() -> None:
    """Verifica se grupos com menos de 5 pessoas sao bloqueados de exibicao."""
    guardrail = PrivacyAndEthicsGuardrail()
    assert guardrail.is_group_protected(headcount=3) is False
    assert guardrail.is_group_protected(headcount=5) is True
    assert guardrail.is_group_protected(headcount=32) is True


def test_individual_query_detection() -> None:
    """Verifica se pedidos por dados individuais de colaboradores sao bloqueados."""
    guardrail = PrivacyAndEthicsGuardrail()

    # Tentativas de violacao que devem ser barradas
    blocked_1, msg_1 = guardrail.inspect_query_for_individual_data(
        "Me mostra os atestados da Carla"
    )
    assert blocked_1 is True
    assert msg_1 is not None
    assert "exclusivamente no nivel de areas" in msg_1

    blocked_2, _ = guardrail.inspect_query_for_individual_data("quem faltou ontem?")
    assert blocked_2 is True

    # Consultas autorizadas sobre areas/times
    allowed_1, msg_ok = guardrail.inspect_query_for_individual_data(
        "Como esta o time de Logistica?"
    )
    assert allowed_1 is False
    assert msg_ok is None
