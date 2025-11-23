from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
import logging
import os
from typing import Any, Dict
import dns.resolver

from app.database import mongodb_ops

app = FastAPI(
    title="AI Guru J Backend",
    description="Backend API for AI Guru J: handles Whisper audio intake, FLAN‑T5 processing, gTTS responses, and tutor interaction endpoints."
)

@app.on_event("startup")
async def startup_event():
    # initialize DB at startup (safe, non-raising)
    mongodb_ops.initialize_db()

@app.get("/")
async def root():
    return {"message": "Welcome to AI Guru J Backend. Visit /docs for API documentation."}

@app.get("/debug/db")
async def debug_db() -> Dict[str, Any]:
    """
    Safe local debug endpoint:
    - reports mongodb_ops init status and ping result
    - attempts SRV and A record resolution for the host in MONGODB_URI
    (Does NOT return credentials.)
    """
    status: Dict[str, Any] = {
        "initialized": mongodb_ops.is_initialized(),
        "reachable": mongodb_ops.check_db_connection(),
    }

    uri = os.getenv("MONGODB_URI", "") or ""
    host = ""
    try:
        if "@" in uri:
            host_part = uri.split("@", 1)[1]
        else:
            # fallback for plain host-only URIs
            host_part = uri
        # strip path/query
        host = host_part.split("/", 1)[0].split("?", 1)[0]
        # mask credentials if present (we only show host)
        status["host"] = host
    except Exception:
        status["host"] = None

    # attempt DNS/SRV resolution for the host (if present)
    if host:
        try:
            srv_name = f"_mongodb._tcp.{host}"
            answers = dns.resolver.resolve(srv_name, "SRV", lifetime=5)
            status["srv_records"] = [
                {"priority": r.priority, "weight": r.weight, "port": r.port, "target": str(r.target).rstrip(".")}
                for r in answers
            ]
        except Exception as e:
            status["srv_records_error"] = str(e)

        try:
            a_answers = dns.resolver.resolve(host, "A", lifetime=5)
            status["a_records"] = [str(r) for r in a_answers]
        except Exception as e:
            status["a_records_error"] = str(e)

    return status

# include tutor router
try:
    from app.api.tutor_router import router as tutor_router
    app.include_router(tutor_router, prefix="/api/tutor", tags=["Tutor Interaction"])
except ImportError:
    logging.getLogger(__name__).warning("app.api.tutor_router not found — tutor routes not included yet.")