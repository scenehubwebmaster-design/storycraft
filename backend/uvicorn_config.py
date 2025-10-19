"""
Optimized Uvicorn server configuration for development and production.

Development mode: Fast reload with single worker
Production mode: Multiple workers for better performance
"""
import multiprocessing
import os

# Determine if we're in development mode
DEV_MODE = os.getenv("DEV_MODE", "true").lower() == "true"

# Server configuration
config = {
    # Explicit package module path prevents ambiguity when starting uvicorn
    # from the repository root or when worker processes import modules.
    "app": "backend.main:app",
    "host": "0.0.0.0",
    "port": 8000,
    "log_level": "info",
    
    # Performance settings
    "loop": "auto",  # Will use uvloop if available (faster than asyncio)
    "http": "auto",  # Will use httptools if available (faster than h11)
    "interface": "asgi3",
    "timeout_keep_alive": 65,
    "limit_concurrency": 1000,
    "backlog": 2048,
}

if DEV_MODE:
    # Development: Enable reload, single worker
    config.update({
        "reload": True,
        "reload_dirs": ["./"],
        "reload_excludes": ["*.pyc", "*.db", "*.log", "__pycache__"],
        "log_level": "info",
    })
else:
    # Production: Multiple workers, no reload
    cpu_count = multiprocessing.cpu_count()
    workers = min(cpu_count * 2 + 1, 16)  # Cap at 16 workers
    
    config.update({
        "workers": workers,
        "log_level": "warning",
        "access_log": False,  # Disable for performance
    })

if __name__ == "__main__":
    import uvicorn
    print(f"Starting Uvicorn server in {'DEVELOPMENT' if DEV_MODE else 'PRODUCTION'} mode")
    print(f"Configuration: {config}")
    uvicorn.run(**config)
