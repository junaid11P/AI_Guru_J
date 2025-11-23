import os
import logging
import datetime # <-- MISSING: Added datetime import for timestamp
from typing import Optional, Dict, Any
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Set logger format
logger = logging.getLogger(__name__)

# Global state variables
_client: Optional[MongoClient] = None
_db = None
_initialized = False

def initialize_db(mongo_uri: Optional[str] = None, server_selection_ms: int = 5000) -> bool:
    """
    Attempt to initialize the MongoDB client. Safe to call at startup.
    Returns True if initialized, False otherwise. Does not raise on failure.
    """
    global _client, _db, _initialized

    if _initialized:
        return True

    # Use URI from argument or environment variable
    uri = mongo_uri or os.getenv("MONGODB_URI", "").strip()
    if not uri:
        logger.warning("MONGODB_URI not set — running with mock DB (no Mongo connection).")
        _initialized = False
        return False

    try:
        _client = MongoClient(
            uri,
            serverSelectionTimeoutMS=server_selection_ms,
            connectTimeoutMS=server_selection_ms,
        )
        
        # quick ping to validate connectivity
        _client.admin.command("ping")
        
        # Use the database specified in the URI, or default to 'ai_guru_j'
        # This fixes the "No default database name defined" error by ensuring a fallback
        _db = _client.get_default_database() or _client.get_database("ai_guru_j_db")
        
        _initialized = True
        logger.info("MongoDB client initialized for database: %s", _db.name)
        return True
    except Exception as exc:
        logger.error("⚠️ Warning: MongoDB client failed to initialize: %s", exc)
        _client = None
        _db = None
        _initialized = False
        return False

def is_initialized() -> bool:
    """Checks if the MongoDB client has been successfully initialized."""
    return _initialized

def check_db_connection(timeout_ms: int = 2000) -> bool:
    """Checks the active MongoDB connection by pinging the server."""
    try:
        if not _initialized or _client is None:
            return False
        # Use a quick timeout for the ping check
        _client.admin.command("ping", maxTimeMS=timeout_ms)
        return True
    except Exception:
        return False

def log_interaction(user_query: str, ai_response_text: str, extras: Optional[Dict[str, Any]] = None) -> None:
    """
    Log an interaction to MongoDB if available; otherwise log locally and no-op.
    This function intentionally does not raise so request handlers remain robust.
    """
    # The 'interactions' collection is explicitly named here
    COLLECTION_NAME = "interactions" 
    
    try:
        if not _initialized or _db is None:
            logger.warning("DB not initialized — skipping log_interaction (mock). Query: %s", user_query[:40] + "...")
            return
        
        doc = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc), # Use datetime
            "query": user_query,
            "response": ai_response_text,
            "extras": extras or {},
        }
        
        # Insert into the named collection
        _db[COLLECTION_NAME].insert_one(doc)
        logger.debug("Interaction logged successfully.")
        
    except PyMongoError as exc:
        # Catch PyMongo errors specifically (network, auth, write failures)
        logger.exception("Failed to write interaction to MongoDB: %s", exc)
    except Exception as exc:
        # Catch other unexpected errors
        logger.exception("An unexpected error occurred during MongoDB logging: %s", exc)