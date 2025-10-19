from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import characters, stories, worlds, llm, generation, settings, locations
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="StoryCraft API", 
    version="1.0.0",
    redirect_slashes=False  # Don't redirect trailing slashes (avoid 307)
)

# Configure CORS
# Use explicit origins when allow_credentials=True; wildcard '*' may be omitted by some browsers
FRONTEND_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
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

@app.get("/health")
def health_check():
    """Health check endpoint"""
    logger.info("Health check endpoint accessed")
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
