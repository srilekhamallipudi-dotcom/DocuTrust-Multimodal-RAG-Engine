import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

CACHE_DIR = Path(__file__).parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)
CACHE_FILE = CACHE_DIR / "response_cache.json"
CACHE_TTL_HOURS = 24  # Cache expires after 24 hours


def hash_question(question: str) -> str:
    """Create a hash of the question for cache key."""
    return hashlib.md5(question.lower().strip().encode()).hexdigest()


def load_cache() -> dict:
    """Load cache from disk."""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Cache load error: {e}")
            return {}
    return {}


def save_cache(cache_data: dict):
    """Save cache to disk."""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache_data, f, indent=2)
    except Exception as e:
        print(f"⚠️ Cache save error: {e}")


def get_cached_response(question: str) -> str or None:
    """Get cached response if available and not expired."""
    cache = load_cache()
    question_hash = hash_question(question)
    
    if question_hash in cache:
        cached_item = cache[question_hash]
        cached_time = datetime.fromisoformat(cached_item.get("timestamp", datetime.now().isoformat()))
        
        # Check if cache is still valid
        if datetime.now() - cached_time < timedelta(hours=CACHE_TTL_HOURS):
            print(f"✅ Cache hit for question: {question[:50]}...")
            return cached_item.get("response")
        else:
            # Cache expired, remove it
            del cache[question_hash]
            save_cache(cache)
    
    return None


def cache_response(question: str, response: str):
    """Cache a response for a question."""
    try:
        cache = load_cache()
        question_hash = hash_question(question)
        
        cache[question_hash] = {
            "question": question,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        
        save_cache(cache)
        print(f"💾 Cached response for question: {question[:50]}...")
    except Exception as e:
        print(f"⚠️ Cache write error: {e}")


def clear_cache():
    """Clear all cached responses."""
    try:
        if CACHE_FILE.exists():
            CACHE_FILE.unlink()
        print("🗑️ Cache cleared")
    except Exception as e:
        print(f"⚠️ Cache clear error: {e}")


def get_cache_stats() -> dict:
    """Get cache statistics."""
    cache = load_cache()
    total_items = len(cache)
    expired_items = 0
    
    for item in cache.values():
        cached_time = datetime.fromisoformat(item.get("timestamp", datetime.now().isoformat()))
        if datetime.now() - cached_time >= timedelta(hours=CACHE_TTL_HOURS):
            expired_items += 1
    
    return {
        "total_cached": total_items,
        "expired": expired_items,
        "active": total_items - expired_items,
        "ttl_hours": CACHE_TTL_HOURS
    }
