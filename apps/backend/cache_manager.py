"""
Cache Manager for KG Explanations

Provides caching for KG explanations and recommendations to improve performance.
Uses LRU cache for KG explanations (long-lived) and TTL cache for user recommendations (short-lived).
"""

from cachetools import LRUCache, TTLCache
from functools import wraps
from typing import Dict, Any, Optional
import threading

# Thread-safe caches
_lock = threading.Lock()

# KG explanation cache (LRU, max 1000 items, long-lived)
kg_explanation_cache = LRUCache(maxsize=1000)

# User recommendation cache (TTL: 5 minutes = 300 seconds)
user_recommendation_cache = TTLCache(maxsize=500, ttl=300)


def cache_kg_explanation(func):
    """
    Decorator to cache KG explanations by item_id
    
    Usage:
        @cache_kg_explanation
        def get_explanation(item_id, ...):
            ...
    """
    @wraps(func)
    def wrapper(item_id, *args, **kwargs):
        with _lock:
            if item_id in kg_explanation_cache:
                return kg_explanation_cache[item_id]
        
        # Compute result
        result = func(item_id, *args, **kwargs)
        
        # Cache it
        with _lock:
            kg_explanation_cache[item_id] = result
        
        return result
    
    return wrapper


def cache_user_recommendations(func):
    """
    Decorator to cache user recommendations by user_id
    
    Usage:
        @cache_user_recommendations
        def get_recommendations(user_id, ...):
            ...
    """
    @wraps(func)
    def wrapper(user_id, *args, **kwargs):
        # Create cache key from user_id and args
        cache_key = f"{user_id}_{hash(str(args))}"
        
        with _lock:
            if cache_key in user_recommendation_cache:
                return user_recommendation_cache[cache_key]
        
        # Compute result
        result = func(user_id, *args, **kwargs)
        
        # Cache it
        with _lock:
            user_recommendation_cache[cache_key] = result
        
        return result
    
    return wrapper


def invalidate_user_cache(user_id: int):
    """
    Invalidate all cached recommendations for a specific user
    
    Args:
        user_id: User ID to invalidate cache for
    """
    with _lock:
        # Remove all entries that start with user_id
        keys_to_remove = [k for k in user_recommendation_cache.keys() if k.startswith(f"{user_id}_")]
        for key in keys_to_remove:
            del user_recommendation_cache[key]


def clear_all_caches():
    """Clear all caches (useful for testing or manual refresh)"""
    with _lock:
        kg_explanation_cache.clear()
        user_recommendation_cache.clear()


def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics
    
    Returns:
        Dictionary with cache sizes and hit rates
    """
    with _lock:
        return {
            "kg_cache_size": len(kg_explanation_cache),
            "kg_cache_maxsize": kg_explanation_cache.maxsize,
            "rec_cache_size": len(user_recommendation_cache),
            "rec_cache_maxsize": user_recommendation_cache.maxsize,
            "rec_cache_ttl": user_recommendation_cache.ttl
        }
