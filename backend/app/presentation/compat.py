"""Camada de compatibilidade transparente para FastAPI e roteadores."""

from typing import Any, Callable, Dict, List, Optional

try:
    from fastapi import APIRouter as _FastAPIRouter
    from fastapi import Depends as _FastAPIDepends
    from fastapi import FastAPI as _FastAPIBase
    from fastapi import HTTPException as _FastAPIHTTPException
    from fastapi import status as _FastAPIStatus
    from fastapi.middleware.cors import CORSMiddleware as _FastAPICORSMiddleware

    HAS_FASTAPI = True
    FastAPI = _FastAPIBase
    APIRouter = _FastAPIRouter
    HTTPException = _FastAPIHTTPException
    status = _FastAPIStatus
    Depends = _FastAPIDepends
    CORSMiddleware = _FastAPICORSMiddleware

except ImportError:
    HAS_FASTAPI = False

    class _Status:
        HTTP_200_OK = 200
        HTTP_201_CREATED = 201
        HTTP_400_BAD_REQUEST = 400
        HTTP_404_NOT_FOUND = 404
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
            self.routes: List[Dict[str, Any]] = []

        def get(self, path: str, *args: Any, **kwargs: Any) -> Callable:
            def decorator(func: Callable) -> Callable:
                self.routes.append({"method": "GET", "path": path, "func": func})
                return func
            return decorator

        def post(self, path: str, *args: Any, **kwargs: Any) -> Callable:
            def decorator(func: Callable) -> Callable:
                self.routes.append({"method": "POST", "path": path, "func": func})
                return func
            return decorator

        def include_router(self, router: Any, *args: Any, **kwargs: Any) -> None:
            self.routes.extend(getattr(router, "routes", []))

    class _FallbackFastAPI(_FallbackRouter):
        def add_middleware(self, *args: Any, **kwargs: Any) -> None:
            pass

    APIRouter = _FallbackRouter  # type: ignore[misc,assignment]
    FastAPI = _FallbackFastAPI  # type: ignore[misc,assignment]

    class CORSMiddleware:  # type: ignore[no-redef]
        pass

    def Depends(dependency: Optional[Callable] = None) -> Any:  # type: ignore[no-redef]
        return dependency() if dependency else None
