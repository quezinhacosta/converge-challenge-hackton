"""Camada de compatibilidade transparente entre Pydantic e Dataclasses da biblioteca padrao."""

import builtins
from typing import Any, Callable, Dict, Optional

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

    def _to_camel(snake_str: str) -> str:
        parts = snake_str.split("_")
        return parts[0] + "".join(p.title() for p in parts[1:])

    class _FieldInfo:
        def __init__(
            self,
            alias: Optional[str] = None,
            default: Any = None,
            default_factory: Any = None,
            **kwargs: Any,
        ) -> None:
            self.alias = alias
            self.default = default
            self.default_factory = default_factory
            self.extra = kwargs

    def Field(*args: Any, **kwargs: Any) -> Any:
        default = args[0] if args else kwargs.get("default")
        return _FieldInfo(
            alias=kwargs.get("alias"),
            default=default,
            default_factory=kwargs.get("default_factory"),
        )

    def model_validator(*args: Any, **kwargs: Any) -> Callable[[Any], Any]:
        def decorator(fn: Any) -> Any:
            fn._is_model_validator = True
            return fn
        return decorator

    class _DataclassBaseModel:
        """Fallback do BaseModel do Pydantic usando inicializacao dinamica e suporte a aliases."""

        def __init__(self, **kwargs: Any) -> None:
            class_annotations = getattr(self.__class__, "__annotations__", {})
            for attr_name in class_annotations:
                class_val = getattr(self.__class__, attr_name, None)
                alias = getattr(class_val, "alias", None)
                camel_name = _to_camel(attr_name)

                val = None
                if attr_name in kwargs:
                    val = kwargs[attr_name]
                elif alias and alias in kwargs:
                    val = kwargs[alias]
                elif camel_name in kwargs:
                    val = kwargs[camel_name]
                elif class_val is not None and hasattr(class_val, "default_factory") and class_val.default_factory:
                    val = class_val.default_factory()
                elif class_val is not None and hasattr(class_val, "default") and class_val.default is not None:
                    val = class_val.default
                setattr(self, attr_name, val)

            for k, v in kwargs.items():
                if not hasattr(self, k):
                    setattr(self, k, v)

            # Executa validadores marcados com @model_validator
            for attr_name in dir(self.__class__):
                attr = getattr(self.__class__, attr_name)
                if getattr(attr, "_is_model_validator", False):
                    attr(self)

        def model_dump(self, *args: Any, by_alias: bool = False, **kwargs: Any) -> builtins.dict[str, Any]:
            result: builtins.dict[str, Any] = {}
            for k, v in self.__dict__.items():
                if k.startswith("_"):
                    continue
                key = k
                class_val = getattr(self.__class__, k, None)
                alias = getattr(class_val, "alias", None)
                if by_alias:
                    if alias:
                        key = alias
                    elif issubclass(self.__class__, ApiModel):
                        key = _to_camel(k)
                if hasattr(v, "model_dump"):
                    result[key] = v.model_dump(by_alias=by_alias)
                elif hasattr(v, "dict"):
                    result[key] = v.dict(by_alias=by_alias)
                elif isinstance(v, list):
                    result[key] = [
                        x.model_dump(by_alias=by_alias) if hasattr(x, "model_dump") else x for x in v
                    ]
                else:
                    result[key] = v
            return result

        def dict(self, *args: Any, by_alias: bool = False, **kwargs: Any) -> builtins.dict[str, Any]:
            return self.model_dump(*args, by_alias=by_alias, **kwargs)

        def __repr__(self) -> str:
            attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items() if not k.startswith("_"))
            return f"{self.__class__.__name__}({attrs})"

    BaseModel = _DataclassBaseModel  # type: ignore[misc,assignment]
    ApiModel = _DataclassBaseModel  # type: ignore[misc,assignment]
