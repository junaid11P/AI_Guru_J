import os
import logging
import datetime
from typing import Optional
from pymongo import MongoClient
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)

_client: Optional[MongoClient] = None
_db = None
_initialized = False

def initialize_db(mongo_uri: Optional[str] = None, server_selection_ms: int = 5000) -> bool:
    """Initialize MongoDB client. Safe to call at startup."""
    global _client, _db, _initialized

    if _initialized:
        return True

    uri = mongo_uri or os.getenv("MONGODB_URI", "").strip()
    if not uri:
        logger.warning("MONGODB_URI not set — running with mock DB.")
        _initialized = False
        return False

    try:
        _client = MongoClient(
            uri,
            serverSelectionTimeoutMS=server_selection_ms,
            connectTimeoutMS=server_selection_ms,
        )
        # Quick connectivity check
        _client.admin.command("ping")
        
        try:
            _db = _client.get_default_database()
        except Exception:
            _db = _client.get_database("ai_guru_j_db")
        
        _initialized = True
        logger.info("MongoDB client initialized: %s", _db.name)
        return True
    except Exception as exc:
        logger.error("MongoDB init failed: %s", exc)
        _client = None
        _db = None
        _initialized = False
        return False

def is_initialized() -> bool:
    return _initialized

def check_db_connection(timeout_ms: int = 2000) -> bool:
    try:
        if not _initialized or _client is None:
            return False
        _client.admin.command("ping", maxTimeMS=timeout_ms)
        return True
    except Exception:
        return False


def log_interaction(user_query: str, explanation: str, code: str, lip_sync: dict, audio_url: str) -> None:
    """
    Logs the full interaction including media links and animation data.
    """
    COLLECTION_NAME = "interactions" 
    
    try:
        if not _initialized or _db is None:
            logger.warning("DB not connected — skipping log.")
            return
        
        doc = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc),
            "user_query": user_query,    # Renamed from 'query' to match your request
            "explanation": explanation,  # Renamed from 'response' to match your request
            "code": code or "",          # Now a top-level field
            "lip_sync": lip_sync or {},  # New Field
            "audio_url": audio_url or "" # New Field
        }
        
        _db[COLLECTION_NAME].insert_one(doc)
        logger.debug("Interaction logged successfully.")
        
    except PyMongoError as exc:
        logger.exception("MongoDB write failed: %s", exc)
    except Exception as exc:
        logger.exception("Unexpected logging error: %s", exc)