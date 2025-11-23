import os
import logging
from typing import Optional, Dict, Any
from pymongo import MongoClient
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)

MONGODB_URI = os.getenv("MONGODB_URI", "").strip()
# Optional: allow quick disable of real DB for local dev
USE_MOCK_DB = os.getenv("USE_MOCK_DB", "0") in ("1", "true", "True")

_client: Optional[MongoClient] = None
_db = None
_initialized = False

if not USE_MOCK_DB and MONGODB_URI:
    try:
        # keep timeouts short so the app doesn't hang on startup
        _client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
        )
        # quick ping to validate connectivity
        _client.admin.command("ping")
        # get default database from the uri if present, otherwise use 'ai_guru_j'
        _db = _client.get_default_database() or _client.get_database("ai_guru_j")
        _initialized = True
        logger.info("MongoDB client initialized.")
    except Exception as exc:
        logger.error("⚠️ Warning: MongoDB client failed to initialize: %s", exc)
        _client = None
        _db = None
        _initialized = False
else:
    if USE_MOCK_DB:
        logger.info("USE_MOCK_DB is set — running with mock DB (no Mongo connection).")
    else:
        logger.warning("MONGODB_URI not set — running with mock DB (no Mongo connection).")

def is_initialized() -> bool:
    return _initialized

def log_interaction(user_query: str, ai_response_text: str, extras: Optional[Dict[str, Any]] = None) -> None:
    """
    Log an interaction to MongoDB if available; otherwise log a local warning and no-op.
    This function intentionally does not raise so it can be used safely in request handlers.
    """
    try:
        if not _initialized or _db is None:
            logger.warning("DB not initialized — skipping log_interaction (mock). Query preview: %s", user_query[:120])
            return

        doc = {
            "query": user_query,
            "response": ai_response_text,
            "extras": extras or {},
        }
        _db.interactions.insert_one(doc)
    except Exception as exc:
        # swallow DB errors but record them in logs
        logger.exception("Failed to write interaction to MongoDB: %s", exc)

def check_db_connection(timeout_ms: int = 2000) -> bool:
    """
    Return True if MongoDB client is initialized and responsive.
    Performs a quick ping; returns False on any error or if client not initialized.
    """
    try:
        if not _initialized or _client is None:
            return False
        _client.admin.command("ping")
        return True
    except Exception:
        return False