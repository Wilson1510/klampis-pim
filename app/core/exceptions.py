from typing import Dict, Any, Optional, List, Union

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


class BaseAPIException(Exception):
    """Base exception for all API errors."""
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class ResourceNotFoundException(BaseAPIException):
    """Exception raised when a requested resource is not found."""
    def __init__(
        self,
        message: str = "Resource not found",
        code: str = "RESOURCE_NOT_FOUND",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class ResourceAlreadyExistsException(BaseAPIException):
    """Exception raised when trying to create a resource that already exists.
    """
    def __init__(
        self,
        message: str = "Resource already exists",
        code: str = "RESOURCE_ALREADY_EXISTS",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=details
        )


class ValidationException(BaseAPIException):
    """Exception raised for validation errors."""
    def __init__(
        self,
        message: str = "Validation error",
        code: str = "VALIDATION_ERROR",
        details: Optional[List[Dict[str, Any]]] = None
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class AuthorizationException(BaseAPIException):
    """Exception raised for authorization errors."""
    def __init__(
        self,
        message: str = "Not authorized",
        code: str = "NOT_AUTHORIZED",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )


class AuthenticationException(BaseAPIException):
    """Exception raised for authentication errors."""
    def __init__(
        self,
        message: str = "Authentication failed",
        code: str = "AUTHENTICATION_FAILED",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )


class InternalServerException(BaseAPIException):
    """Exception raised for server errors."""
    def __init__(
        self,
        message: str = "Internal server error",
        code: str = "INTERNAL_SERVER_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


def format_error_response(
    code: str,
    message: str,
    details: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Format error response following API standards."""
    return {
        "success": False,
        "data": None,
        "error": {
            "code": code,
            "message": message,
            "details": details
        }
    }


async def base_exception_handler(
    request: Request,
    exc: BaseAPIException
) -> JSONResponse:
    """Handle API exceptions and return formatted response."""
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(
            code=exc.code,
            message=exc.message,
            details=exc.details
        )
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException
) -> JSONResponse:
    """Handle HTTP exceptions and return formatted response."""
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(
            code=f"HTTP_ERROR_{exc.status_code}",
            message=str(exc.detail)
        )
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle validation exceptions and return formatted response."""
    errors = []
    for error in exc.errors():
        errors.append({
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", "")
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=format_error_response(
            code="VALIDATION_ERROR",
            message="Validation error",
            details=errors
        )
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app."""
    app.add_exception_handler(BaseAPIException, base_exception_handler)
    app.add_exception_handler(
        StarletteHTTPException,
        http_exception_handler
    )
    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler
    )
