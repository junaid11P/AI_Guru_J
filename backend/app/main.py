from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import mongodb_ops
from app.api.tutor_router import router as tutor_router

# Set up basic logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Guru J Backend",
    description="Backend API for AI Guru J deployed on Render."
)

# PERMISSIVE CORS FOR DEBUGGING
# 'allow_origins=["*"]' is only compatible with 'allow_credentials=False'
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    import shutil
    mongodb_ops.initialize_db()
    rhubarb_path = os.getenv("RHUBARB_BINARY", "rhubarb")
    if not shutil.which(rhubarb_path):
        logging.warning(f"⚠️ Rhubarb binary not found in path: {rhubarb_path}")

@app.get("/")
async def root():
    return {"message": "AI Guru J Backend is Live!"}

app.include_router(tutor_router, prefix="/api/tutor", tags=["Tutor Interaction"])