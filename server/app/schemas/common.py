from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorResponse(BaseModel):
    """Shape returned by every error response, regardless of source
    (validation, not-found, unhandled exception, etc.) — see the exception
    handlers registered in main.py."""

    success: bool = False
    message: str
    errors: list[dict[str, Any]] | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    skip: int
    limit: int
