from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
try:
    # Preferred (when package is importable)
    from .database import engine, Base
    from .routers import characters, stories, worlds, llm, generation, settings, locations, references, monsters, chat, game, combat, campaigns, checkpoints, adventures, openai_audio, user_settings
except Exception:
    # Fallback to absolute imports so running `python backend/main.py` or
    # starting uvicorn from other working directories still works. Ensure the
    # repository root is on sys.path so the `backend` package can be imported.
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from backend.database import engine, Base
    from backend.routers import characters, stories, worlds, llm, generation, settings, locations, references, monsters, chat, game, combat, campaigns, checkpoints, adventures, openai_audio, user_settings
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
app.include_router(monsters.router, tags=["monsters"])  # /api/monsters/
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])  # /api/chat/
app.include_router(game.router, tags=["game"])  # /api/game/ - D&D game session management
app.include_router(combat.router, prefix="/api/combat", tags=["combat"])  # /api/combat/ - Combat encounters
app.include_router(campaigns.router, tags=["campaigns"])  # /api/campaigns/ - D&D Campaign management
app.include_router(checkpoints.router, tags=["checkpoints"])  # /api/checkpoints/ - Campaign checkpoint system
app.include_router(adventures.router, tags=["adventures"])  # /api/adventures/ - Adventure templates for campaign creation
app.include_router(openai_audio.router, tags=["audio"])  # /api/audio/ - OpenAI TTS and Whisper services
app.include_router(user_settings.router, tags=["user-settings"])  # /api/settings/ - User preferences and settings


@app.on_event("startup")
async def _populate_groq_model_cache():
    """Fetch available Groq models at startup and cache them for rate limiter use.

    This call is best-effort: if GROQ_API_KEY isn't set or the network call
    fails, the groq_models module will fall back to hardcoded defaults.
    """
    lg = logging.getLogger("backend.main")
    try:
        from backend import groq_models
        from backend import model_cache

        try:
            models = await groq_models.fetch_available_models()
        except TypeError:
            # Some environments may have a synchronous fallback
            models = groq_models.fetch_available_models()

        if models:
            model_cache.set_models("groq", models)
            lg.info(f"Cached {len(models)} Groq models on startup")
        else:
            lg.info("Groq model fetch returned no models; using fallback list")
    except Exception as e:
        lg.info(f"Groq model prefetch skipped: {e}")

@app.get("/health")
def health_check():
    """Health check endpoint"""
    logger.info("Health check endpoint accessed")
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
