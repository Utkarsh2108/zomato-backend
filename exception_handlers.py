# exception_handlers.py

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from jwt.exceptions import PyJWTError
import logging
from typing import Union

from exceptions import BaseCustomException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_error_response(
    status_code: int,
    message: str,
    error_type: str = "error",
    details: dict = None,
    request_id: str = None) -> JSONResponse:
    """Create standardized error response"""
    error_response = {
        "success": False,
        "error": {
            "type": error_type,
            "message": message,
            "status_code": status_code
        }
    }   
    
    if details:
        error_response["error"]["details"] = details
    
    if request_id:
        error_response["request_id"] = request_id
        
    return JSONResponse(
        status_code=status_code,
        content=error_response
    )


async def custom_exception_handler(request: Request, exc: BaseCustomException) -> JSONResponse:
    """Handle custom application exceptions"""
    logger.error(f"Custom exception occurred: {exc.message}", exc_info=True)
    
    return create_error_response(
        status_code=exc.status_code,
        message=exc.message,
        error_type=type(exc).__name__,
        details=exc.details,
        request_id=getattr(request.state, 'request_id', None)
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions"""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    
    return create_error_response(
        status_code=exc.status_code,
        message=exc.detail,
        error_type="HTTPException",
        request_id=getattr(request.state, 'request_id', None)
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors"""
    logger.warning(f"Validation error: {exc.errors()}")
    
    # Format validation errors for better readability
    formatted_errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        formatted_errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"],
            "input": error.get("input")
        })
    
    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Request validation failed",
        error_type="ValidationError",
        details={"validation_errors": formatted_errors},
        request_id=getattr(request.state, 'request_id', None)
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle SQLAlchemy database exceptions"""
    logger.error(f"Database error occurred: {str(exc)}", exc_info=True)
    
    # Don't expose internal database errors to users in production
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="An internal database error occurred",
        error_type="DatabaseError",
        request_id=getattr(request.state, 'request_id', None)
    )


async def jwt_exception_handler(request: Request, exc: PyJWTError) -> JSONResponse:
    """Handle JWT-related exceptions"""
    logger.warning(f"JWT error: {str(exc)}")
    
    return create_error_response(
        status_code=status.HTTP_401_UNAUTHORIZED,
        message="Invalid or expired authentication token",
        error_type="AuthenticationError",
        request_id=getattr(request.state, 'request_id', None)
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error occurred: {str(exc)}", exc_info=True)
    
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="An unexpected error occurred",
        error_type="InternalServerError",
        request_id=getattr(request.state, 'request_id', None)
    )


def register_exception_handlers(app):
    """Register all exception handlers with the FastAPI app"""
    
    # Custom exceptions
    app.add_exception_handler(BaseCustomException, custom_exception_handler)
    
    # FastAPI built-in exceptions
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # Third-party exceptions
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(PyJWTError, jwt_exception_handler)
    
    # Catch-all for unexpected exceptions
    app.add_exception_handler(Exception, general_exception_handler)