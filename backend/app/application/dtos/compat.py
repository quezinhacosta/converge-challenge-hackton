"""Camada de compatibilidade transparente entre Pydantic e Dataclasses da biblioteca padrao."""

from typing import Any, Callable, Dict, Type, TypeVar

try:
    from pydantic import BaseModel as _PydanticBaseModel
    from pydantic import Field as _PydanticField

    HAS_PYDANTIC = True
    BaseModel = _PydanticBaseModel
    Field = _PydanticField

except ImportError:
    HAS_PYDANTIC = False
    from dataclasses import dataclass, field

    def Field(*args: Any, **kwargs: Any) -> Any:
        """Fallback do Pydantic Field usando dataclasses.field."""
        default = kwargs.get("default")
        default_factory = kwargs.get("default_factory")
        if default_factory is not None:
            return field(default_factory=default_factory)
        if default is not None:
            return field(default=default)
        return field()

    class _DataclassBaseModel:
        """Fallback do BaseModel do Pydantic usando inicializacao dinamica."""

        def __init__(self, **kwargs: Any) -> None:
            for k, v in kwargs.items():
                setattr(self, k, v)

        def dict(self) -> Dict[str, Any]:
            return self.__dict__.copy()

        def model_dump(self) -> Dict[str, Any]:
            return self.__dict__.copy()

        def __repr__(self) -> str:
            attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
            return f"{self.__class__.__name__}({attrs})"

    BaseModel = _DataclassBaseModel  # type: ignore[misc,assignment]
