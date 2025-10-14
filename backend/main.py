from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import characters, stories, worlds, llm, generation, settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StoryCraft API",
    description="AI-powered story creation backend",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",  # Vite alternate port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(characters.router, prefix="/api/characters", tags=["characters"])
app.include_router(stories.router, prefix="/api/stories", tags=["stories"])
app.include_router(worlds.router, prefix="/api/worlds", tags=["worlds"])
app.include_router(llm.router, prefix="/api/llm", tags=["llm"])
app.include_router(generation.router, tags=["generation"])
app.include_router(settings.router, tags=["settings"])

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to StoryCraft API",
        "version": "0.1.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    logger.info("Health check endpoint accessed")
    return {"status": "healthy"}
