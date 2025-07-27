"""
Response helper utilities for standardized API responses.
"""
import math
from typing import List, TypeVar, Optional, Any, Dict

from app.schemas.base import (
    SingleItemResponse,
    MultipleItemsResponse,
    MetaSchema,
    ErrorDetailSchema
)

T = TypeVar('T')


def create_single_item_response(
    data: T,
    success: bool = True
) -> SingleItemResponse[T]:
    """
    Create a standardized single item response.

    Args:
        data: The response data
        success: Whether the request was successful

    Returns:
        StandardizedResponse with single item format
    """
    return SingleItemResponse[T](
        success=success,
        data=data,
        error=None
    )


def create_multiple_items_response(
    data: List[T],
    page: int,
    limit: int,
    total: int,
    success: bool = True
) -> MultipleItemsResponse[T]:
    """
    Create a standardized multiple items response with pagination.

    Args:
        data: List of response data
        page: Current page number
        limit: Items per page
        total: Total number of items
        success: Whether the request was successful

    Returns:
        StandardizedResponse with multiple items format and pagination metadata
    """
    pages = math.ceil(total / limit)

    meta = MetaSchema(
        page=page,
        limit=limit,
        total=total,
        pages=pages
    )

    return MultipleItemsResponse[T](
        success=success,
        data=data,
        meta=meta,
        error=None
    )


def create_error_response(
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    success: bool = False
) -> SingleItemResponse[None]:
    """
    Create a standardized error response.

    Args:
        code: Error code
        message: Error message
        details: Additional error details
        success: Whether the request was successful (typically False for errors)

    Returns:
        StandardizedResponse with error format
    """
    error = ErrorDetailSchema(
        code=code,
        message=message,
        details=details
    )

    return SingleItemResponse[None](
        success=success,
        data=None,
        error=error
    )
