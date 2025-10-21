from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
try:
    # Preferred (when package is importable)
    from .database import engine, Base
    from .routers import characters, stories, worlds, llm, generation, settings, locations, references
except Exception:
    # Fallback to absolute imports so running `python backend/main.py` or
    # starting uvicorn from other working directories still works. Ensure the
    # repository root is on sys.path so the `backend` package can be imported.
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from backend.database import engine, Base
    from backend.routers import characters, stories, worlds, llm, generation, settings, locations, references
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optionally run local development migrations (non-production safe)
# Controlled by env var RUN_LOCAL_MIGRATIONS=true
if os.environ.get("RUN_LOCAL_MIGRATIONS", "false").lower() == "true":
    try:
        # Import and run the lightweight migration helper via package import
        from backend.scripts import ensure_softdelete_columns as _migrate

        logger.info("RUN_LOCAL_MIGRATIONS=true: ensuring soft-delete columns")
        _migrate.main()
    except Exception as e:
        logger.exception("Local migration helper failed: %s", e)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="StoryCraft API", 
    version="1.0.0",
    redirect_slashes=False  # Don't redirect trailing slashes (avoid 307)
)

# Configure CORS
# FRONTEND_ORIGINS can be set via environment variable as a comma-separated
# list of origins (e.g. "http://localhost:3000,http://192.168.250.11:3000").
# If the env var is not set, fall back to a sensible local-dev default.
_default_frontend_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # Local network dev host - add your machine IP/hostname as needed
    "http://192.168.250.11:3000",
]

_env_val = os.environ.get("FRONTEND_ORIGINS", "").strip()
if _env_val:
    # Split on comma, trim whitespace, and ignore empty parts
    FRONTEND_ORIGINS = [o.strip() for o in _env_val.split(",") if o.strip()]
else:
    FRONTEND_ORIGINS = _default_frontend_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(characters.router, prefix="/api/characters", tags=["characters"])
app.include_router(stories.router, prefix="/api/stories", tags=["stories"])
app.include_router(worlds.router, prefix="/api/worlds", tags=["worlds"])
app.include_router(llm.router, prefix="/api/llm", tags=["llm"])
app.include_router(generation.router, tags=["generation"])  # No prefix - already defined in router
app.include_router(settings.router, tags=["settings"])  # No prefix - already defined in router
app.include_router(locations.router, tags=["locations"])  # /api/locations/
app.include_router(references.router, tags=["references"])  # /api/references/

@app.get("/health")
def health_check():
    """Health check endpoint"""
    logger.info("Health check endpoint accessed")
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
