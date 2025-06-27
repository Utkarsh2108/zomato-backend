# exceptions.py

from fastapi import status
from typing import Optional, Any, Dict

class BaseCustomException(Exception):
    """""
     Base exception class for custom exceptions.
 
     Args:
         message (str): The error message describing the exception.
         status_code (int, optional): HTTP status code associated with the exception. Defaults to 500.
         details (Optional[Dict[str, Any]], optional): Additional information about the exception, such as context or metadata. Defaults to None.
     """""
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


# Authentication & Authorization Exceptions
class AuthenticationException(BaseCustomException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, details)


class AuthorizationException(BaseCustomException):
    """Raised when user lacks permission for an action"""
    
    def __init__(self, message: str = "Insufficient permissions", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_403_FORBIDDEN, details)


class InvalidTokenException(AuthenticationException):
    """Raised when JWT token is invalid or expired"""
    
    def __init__(self, message: str = "Invalid or expired token", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


# User-related Exceptions
class UserNotFoundException(BaseCustomException):
    """Raised when user is not found"""
    
    def __init__(self, user_id: Optional[int] = None, email: Optional[str] = None):
        if user_id:
            message = f"User with ID {user_id} not found"
        elif email:
            message = f"User with email {email} not found"
        else:
            message = "User not found"
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class UserAlreadyExistsException(BaseCustomException):
    """Raised when trying to create a user that already exists"""
    
    def __init__(self, email: str):
        message = f"User with email {email} already exists"
        super().__init__(message, status.HTTP_409_CONFLICT)


class InvalidCredentialsException(AuthenticationException):
    """Raised when login credentials are invalid"""
    
    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message)


# Restaurant-related Exceptions
class RestaurantNotFoundException(BaseCustomException):
    """Raised when restaurant is not found"""
    
    def __init__(self, restaurant_id: int):
        message = f"Restaurant with ID {restaurant_id} not found"
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class RestaurantInactiveException(BaseCustomException):
    """Raised when trying to access an inactive restaurant"""
    
    def __init__(self, restaurant_id: int):
        message = f"Restaurant with ID {restaurant_id} is currently inactive"
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


# Menu-related Exceptions
class MenuItemNotFoundException(BaseCustomException):
    """Raised when menu item is not found"""
    
    def __init__(self, item_id: int):
        message = f"Menu item with ID {item_id} not found"
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class MenuItemUnavailableException(BaseCustomException):
    """Raised when menu item is unavailable"""
    
    def __init__(self, item_id: int):
        message = f"Menu item with ID {item_id} is currently unavailable"
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


# Order-related Exceptions
class OrderNotFoundException(BaseCustomException):
    """Raised when order is not found"""
    
    def __init__(self, order_id: int):
        message = f"Order with ID {order_id} not found"
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class OrderNotCancellableException(BaseCustomException):
    """Raised when trying to cancel an order that cannot be cancelled"""
    
    def __init__(self, order_id: int, current_status: str):
        message = f"Order {order_id} cannot be cancelled. Current status: {current_status}"
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class OrderAccessDeniedException(AuthorizationException):
    """Raised when user tries to access an order they don't own"""
    
    def __init__(self, order_id: int):
        message = f"Access denied for order {order_id}"
        super().__init__(message)


class InvalidOrderStatusException(BaseCustomException):
    """Raised when trying to set an invalid order status"""
    
    def __init__(self, status_value: str):
        message = f"Invalid order status: {status_value}"
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class EmptyCartException(BaseCustomException):
    """Raised when trying to place an order with empty cart"""
    
    def __init__(self):
        message = "Cannot place order with empty cart"
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


# Review-related Exceptions
class ReviewNotFoundException(BaseCustomException):
    """Raised when review is not found"""
    
    def __init__(self, review_id: int):
        message = f"Review with ID {review_id} not found"
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ReviewAlreadyExistsException(BaseCustomException):
    """Raised when user tries to review a restaurant they've already reviewed"""
    
    def __init__(self, restaurant_id: int):
        message = f"You have already submitted a review for restaurant {restaurant_id}"
        super().__init__(message, status.HTTP_409_CONFLICT)


class ReviewNotAllowedException(BaseCustomException):
    """Raised when user tries to review without completed order"""
    
    def __init__(self, restaurant_id: int):
        message = f"You can only review restaurant {restaurant_id} after completing an order"
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class ReviewAccessDeniedException(AuthorizationException):
    """Raised when user tries to modify a review they don't own"""
    
    def __init__(self, review_id: int):
        message = f"Access denied for review {review_id}"
        super().__init__(message)


# Favorite-related Exceptions
class FavoriteNotFoundException(BaseCustomException):
    """Raised when favorite is not found"""
    
    def __init__(self, restaurant_id: int):
        message = f"Favorite for restaurant {restaurant_id} not found"
        super().__init__(message, status.HTTP_404_NOT_FOUND)


# Database-related Exceptions
class DatabaseException(BaseCustomException):
    """Raised when database operation fails"""
    
    def __init__(self, message: str = "Database operation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR, details)


class ValidationException(BaseCustomException):
    """Raised when input validation fails"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else {}
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, details)


# Search-related Exceptions
class SearchException(BaseCustomException):
    """Raised when search operation fails"""
    
    def __init__(self, message: str = "Search operation failed"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class InvalidSearchParametersException(BaseCustomException):
    """Raised when search parameters are invalid"""
    
    def __init__(self, message: str = "Invalid search parameters"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)