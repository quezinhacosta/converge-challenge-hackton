"""Camada de compatibilidade transparente para FastAPI, roteadores e TestClient."""

import inspect
import json
import re
from collections.abc import Callable
from datetime import date, datetime
from typing import Any

try:
    from fastapi import APIRouter as _FastAPIRouter
    from fastapi import Depends as _FastAPIDepends
    from fastapi import FastAPI as _FastAPIBase
    from fastapi import HTTPException as _FastAPIHTTPException
    from fastapi import status as _FastAPIStatus
    from fastapi.middleware.cors import CORSMiddleware as _FastAPICORSMiddleware
    from fastapi.testclient import TestClient as _FastAPITestClient

    HAS_FASTAPI = True
    FastAPI = _FastAPIBase
    APIRouter = _FastAPIRouter
    HTTPException = _FastAPIHTTPException
    status = _FastAPIStatus
    Depends = _FastAPIDepends
    CORSMiddleware = _FastAPICORSMiddleware
    TestClient = _FastAPITestClient

except ImportError:
    HAS_FASTAPI = False

    class _Status:
        HTTP_200_OK = 200
        HTTP_201_CREATED = 201
        HTTP_400_BAD_REQUEST = 400
        HTTP_404_NOT_FOUND = 404
        HTTP_409_CONFLICT = 409
        HTTP_422_UNPROCESSABLE_ENTITY = 422
        HTTP_500_INTERNAL_SERVER_ERROR = 500
        HTTP_501_NOT_IMPLEMENTED = 501

    status = _Status()  # type: ignore[assignment]

    class HTTPException(Exception):  # type: ignore[no-redef]
        def __init__(self, status_code: int, detail: str) -> None:
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    class _FallbackRouter:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self.routes: list[dict[str, Any]] = []

        def get(self, path: str, *args: Any, **kwargs: Any) -> Callable:
            def decorator(func: Callable) -> Callable:
                self.routes.append({"method": "GET", "path": path, "func": func, "kwargs": kwargs})
                return func
            return decorator

        def post(self, path: str, *args: Any, **kwargs: Any) -> Callable:
            def decorator(func: Callable) -> Callable:
                self.routes.append({"method": "POST", "path": path, "func": func, "kwargs": kwargs})
                return func
            return decorator

        def include_router(self, router: Any, prefix: str = "", *args: Any, **kwargs: Any) -> None:
            for route in getattr(router, "routes", []):
                sub_path = route["path"].lstrip("/")
                prefix_clean = prefix.rstrip("/")
                if sub_path:
                    full_path = f"{prefix_clean}/{sub_path}"
                else:
                    full_path = prefix_clean or "/"
                self.routes.append({
                    "method": route["method"],
                    "path": full_path,
                    "func": route["func"],
                    "kwargs": route.get("kwargs", {}),
                })

    class _FallbackFastAPI(_FallbackRouter):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)
            self.dependency_overrides: dict[Any, Any] = {}
            self.state: Any = type("_State", (), {})()

        def add_middleware(self, *args: Any, **kwargs: Any) -> None:
            pass

    APIRouter = _FallbackRouter  # type: ignore[misc,assignment]
    FastAPI = _FallbackFastAPI  # type: ignore[misc,assignment]

    class CORSMiddleware:  # type: ignore[no-redef]
        pass

    class DependsHolder:
        def __init__(self, dependency: Callable | None = None) -> None:
            self.dependency = dependency

    def Depends(dependency: Callable | None = None) -> Any:  # type: ignore[no-redef]
        return DependsHolder(dependency)

    class _TestResponse:
        def __init__(self, status_code: int, data: Any) -> None:
            self.status_code = status_code
            self._data = data
            if isinstance(data, (dict, list)):
                self.text = json.dumps(data, default=str)
            else:
                self.text = str(data)

        def json(self) -> Any:
            return self._data

    class TestClient:  # type: ignore[no-redef]
        """TestClient em memoria para execucao direta de testes de integracao."""

        __test__ = False

        def __init__(self, app: Any) -> None:
            self.app = app

        def __enter__(self) -> Any:
            return self

        def __exit__(self, *args: Any) -> None:
            pass

        def _dispatch(self, method: str, url: str, json_data: Any = None) -> _TestResponse:
            url_clean = url.split("?")[0].rstrip("/")
            if not url_clean:
                url_clean = "/"

            for route in self.app.routes:
                if route["method"] != method:
                    continue
                route_pattern = re.sub(r"\{([a-zA-Z0-9_]+)\}", r"(?P<\1>[^/]+)", route["path"].rstrip("/") or "/")
                regex = f"^{route_pattern}$"
                match = re.match(regex, url_clean)
                if match:
                    path_params = match.groupdict()
                    handler = route["func"]
                    sig = inspect.signature(handler)
                    call_args: dict[str, Any] = {}

                    try:
                        for param_name, param in sig.parameters.items():
                            if param_name in path_params:
                                call_args[param_name] = path_params[param_name]
                            elif isinstance(param.default, DependsHolder) or (param.default.__class__.__name__ == "DependsHolder"):
                                dep_fn = param.default.dependency
                                override_fn = self.app.dependency_overrides.get(dep_fn, dep_fn)
                                call_args[param_name] = override_fn() if override_fn else None
                            elif param_name == "payload" or param.annotation not in (inspect.Parameter.empty, str, int, float, bool):
                                ann = param.annotation
                                if json_data is not None:
                                    if hasattr(ann, "__call__") and ann is not dict:
                                        try:
                                            call_args[param_name] = ann(**json_data)
                                        except Exception as e:
                                            return _TestResponse(422, {"detail": str(e)})
                                    else:
                                        call_args[param_name] = json_data
                                else:
                                    call_args[param_name] = None

                        res = handler(**call_args)
                        status_code = route.get("kwargs", {}).get("status_code", 200)

                        def _dump(val: Any) -> Any:
                            if isinstance(val, (datetime, date)):
                                return val.isoformat()
                            if hasattr(val, "model_dump"):
                                return _dump(val.model_dump(by_alias=True))
                            if hasattr(val, "dict"):
                                return _dump(val.dict(by_alias=True))
                            if isinstance(val, list):
                                return [_dump(x) for x in val]
                            if isinstance(val, dict):
                                return {k: _dump(v) for k, v in val.items()}
                            return val

                        return _TestResponse(status_code, _dump(res))

                    except HTTPException as http_exc:
                        return _TestResponse(http_exc.status_code, {"detail": http_exc.detail})
                    except ValueError as val_exc:
                        return _TestResponse(422, {"detail": str(val_exc)})
                    except Exception as exc:
                        if exc.__class__.__name__ == "CardStateError":
                            return _TestResponse(409, {"detail": str(exc)})
                        return _TestResponse(500, {"detail": str(exc)})

            return _TestResponse(404, {"detail": f"Rota {method} {url} nao encontrada."})

        def get(self, url: str, **kwargs: Any) -> _TestResponse:
            return self._dispatch("GET", url)

        def post(self, url: str, json: Any = None, **kwargs: Any) -> _TestResponse:
            return self._dispatch("POST", url, json_data=json)

        def request(self, method: str, url: str, json: Any = None, **kwargs: Any) -> _TestResponse:
            return self._dispatch(method.upper(), url, json_data=json)
