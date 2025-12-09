import functools
import hashlib
import json
import logging
from typing import Callable, TypeVar, ParamSpec, Awaitable, Any
from enum import Enum
from app.core.cache import cache_manager

# Type variables for proper decorator typing
P = ParamSpec('P')  # Captures function parameters
R = TypeVar('R')    # Captures return type

logger = logging.getLogger(__name__)

def _serialize_value(value: Any) -> str:
    """
    Serialize a value to a deterministic string for cache key generation.
    
    Handles special cases like:
    - Database sessions (skip them)
    - Enums (use their value)
    - None values
    - Lists, dicts, and primitives
    """
    if value is None:
        return "None"
    
    # Skip database sessions and other non-serializable objects
    if hasattr(value, '__class__'):
        class_name = value.__class__.__name__
        if 'Session' in class_name or 'AsyncSession' in class_name:
            return ""  # Don't include session in cache key
    
    # Handle Enums - use their value
    if isinstance(value, Enum):
        return str(value.value)
    
    # Handle primitives
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    
    # Handle None
    if value is None:
        return "None"
    
    # Handle lists/tuples
    if isinstance(value, (list, tuple)):
        return json.dumps([_serialize_value(v) for v in value], sort_keys=True)  # type: ignore[misc]
    
    # Handle dicts
    if isinstance(value, dict):
        return json.dumps({k: _serialize_value(v) for k, v in value.items()}, sort_keys=True)  # type: ignore[misc]
    
    # Fallback: try to convert to string
    return str(value)

def _generate_cache_key(func_name: str, key_prefix: str, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
    """
    Generate a deterministic cache key from function arguments.
    
    Skips the first argument if it's a 'self' instance.
    """
    key_parts = [key_prefix, func_name]
    
    # Process args (skip 'self' if it's the first argument)
    start_idx = 1 if args and hasattr(args[0], '__class__') and hasattr(args[0].__class__, '__mro__') else 0
    for arg in args[start_idx:]:
        serialized = _serialize_value(arg)
        if serialized:  # Only add non-empty serializations
            key_parts.append(serialized)
    
    # Process kwargs in sorted order for consistency
    for key in sorted(kwargs.keys()):
        value = kwargs[key]
        serialized = _serialize_value(value)
        if serialized:  # Only add non-empty serializations
            key_parts.append(f"{key}={serialized}")
    
    # Join all parts and create hash
    cache_key_data = ":".join(key_parts)
    cache_key = hashlib.md5(cache_key_data.encode()).hexdigest()
    
    return cache_key

def cache_result(ttl: int = 3600, key_prefix: str = "") -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """
    Decorator to cache async function results.
    
    Args:
        ttl: Time to live for cached results in seconds (default: 3600)
        key_prefix: Prefix for cache keys (default: "")
    
    Returns:
        Decorator function that wraps async functions with caching
    
    Example:
        @cache_result(ttl=600, key_prefix="user")
        async def get_user(user_id: int) -> UserResponse:
            return await fetch_user(user_id)
    """
    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # Generate deterministic cache key
            cache_key = _generate_cache_key(func.__name__, key_prefix, args, kwargs)  # type: ignore[arg-type]
            logger.info(f"🔑 Cache key: {cache_key} for {func.__name__}")

            # Try to get from cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                logger.info(f"✅ Cache HIT for {func.__name__}")
                return cached_result  # type: ignore[return-value]
        
            logger.info(f"❌ Cache MISS for {func.__name__}")

            # Execute function and cache result
            result = await func(*args, **kwargs)
            success = await cache_manager.set(cache_key, result, ttl)  # type: ignore[arg-type]
            logger.info(f"Cache set success: {success} for key: {cache_key}")

            return result
        return wrapper
    return decorator
