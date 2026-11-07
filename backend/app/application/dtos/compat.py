"""Camada de compatibilidade transparente entre Pydantic e Dataclasses da biblioteca padrao."""

import builtins
from typing import Any, Callable

try:
    from pydantic import BaseModel as _PydanticBaseModel
    from pydantic import ConfigDict as _ConfigDict
    from pydantic import Field as _PydanticField
    from pydantic import model_validator as _PydanticModelValidator
    from pydantic.alias_generators import to_camel as _to_camel

    HAS_PYDANTIC = True
    BaseModel = _PydanticBaseModel
    Field = _PydanticField
    model_validator = _PydanticModelValidator

    class ApiModel(_PydanticBaseModel):
        """DTO de API: aceita snake_case ou camelCase na entrada e responde em camelCase.

        O frontend Angular usa camelCase; o codigo Python continua usando snake_case.
        """

        model_config = _ConfigDict(alias_generator=_to_camel, populate_by_name=True)

except ImportError:
    HAS_PYDANTIC = False
    from dataclasses import field

    def Field(*args: Any, **kwargs: Any) -> Any:
        """Fallback do Pydantic Field usando dataclasses.field."""
        default = kwargs.get("default")
        default_factory = kwargs.get("default_factory")
        if default_factory is not None:
            return field(default_factory=default_factory)
        if default is not None:
            return field(default=default)
        return field()

    def model_validator(*args: Any, **kwargs: Any) -> Callable[[Any], Any]:
        """Fallback do Pydantic model_validator como no-op decorator."""
        def decorator(fn: Any) -> Any:
            return fn
        return decorator

    class _DataclassBaseModel:
        """Fallback do BaseModel do Pydantic usando inicializacao dinamica."""

        def __init__(self, **kwargs: Any) -> None:
            for k, v in kwargs.items():
                setattr(self, k, v)

        def dict(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
            return self.__dict__.copy()

        def model_dump(self, *args: Any, **kwargs: Any) -> builtins.dict[str, Any]:
            return self.__dict__.copy()

        def __repr__(self) -> str:
            attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
            return f"{self.__class__.__name__}({attrs})"

    BaseModel = _DataclassBaseModel  # type: ignore[misc,assignment]
    ApiModel = _DataclassBaseModel  # type: ignore[misc,assignment]
