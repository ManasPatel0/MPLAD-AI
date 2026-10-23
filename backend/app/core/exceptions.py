"""Standard exception classes and FastAPI exception handlers matching API_CONTRACTS.md."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def utc_now_iso() -> str:
    """Return ISO-8601 formatted UTC timestamp with Z suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class AppException(Exception):
    """Base application exception following the MPLAD-AI contract."""

    def __init__(
        self,
        detail: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_SERVER_ERROR",
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code
        self.extra = extra or {}


class NotFoundException(AppException):
    def __init__(self, detail: str = "Requested resource not found", extra: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            extra=extra,
        )


class ConflictException(AppException):
    def __init__(self, detail: str = "Resource conflict detected", extra: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_409_CONFLICT,
            error_code="RESOURCE_CONFLICT",
            extra=extra,
        )


class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Authentication credentials required", extra: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
            extra=extra,
        )


class ForbiddenException(AppException):
    def __init__(self, detail: str = "Insufficient permissions for requested action", extra: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
            extra=extra,
        )


class BadRequestException(AppException):
    def __init__(self, detail: str = "Invalid request payload", extra: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="BAD_REQUEST",
            extra=extra,
        )


def register_exception_handlers(app: FastAPI) -> None:
    """Register uniform JSON exception handlers on the FastAPI application."""

    @app.exception_handler(AppException)
    async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
        content: Dict[str, Any] = {
            "detail": exc.detail,
            "error_code": exc.error_code,
            "timestamp": utc_now_iso(),
        }
        if exc.extra:
            content.update(exc.extra)
        return JSONResponse(status_code=exc.status_code, content=content)

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "RESOURCE_NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            409: "RESOURCE_CONFLICT",
            422: "UNPROCESSABLE_ENTITY",
            500: "INTERNAL_SERVER_ERROR",
        }
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": str(exc.detail),
                "error_code": code_map.get(exc.status_code, "HTTP_ERROR"),
                "timestamp": utc_now_iso(),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        errors = exc.errors()
        message = errors[0].get("msg") if errors else "Validation error in request"
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": f"Validation failed: {message}",
                "error_code": "VALIDATION_ERROR",
                "timestamp": utc_now_iso(),
                "validation_errors": errors,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled server exception: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An unexpected internal server error occurred.",
                "error_code": "INTERNAL_SERVER_ERROR",
                "timestamp": utc_now_iso(),
            },
        )
