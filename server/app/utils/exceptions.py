from typing import Any


class AppError(Exception):
    """Base class for application errors that the central handler in main.py
    converts into a consistent ErrorResponse payload."""

    status_code = 400

    def __init__(self, message: str, details: list[dict[str, Any]] | None = None) -> None:
        self.message = message
        self.details = details
        super().__init__(message)


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409


class UnsupportedFileTypeError(AppError):
    status_code = 415


class PayloadTooLargeError(AppError):
    status_code = 413


class ExtractionError(AppError):
    status_code = 422
