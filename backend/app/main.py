from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .api.router import router
from .services.gemini_client import log_gemini_startup_status
from .services.simulator import simulator
from .db.database import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Intelligent Care Assistant backend")
    
    # Initialize database
    try:
        init_db()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    log_gemini_startup_status()
    await simulator.start()
    logger.info("IoT simulator started")
    try:
        yield
    finally:
        logger.info("Stopping Intelligent Care Assistant backend")
        await simulator.stop()
        logger.info("IoT simulator stopped")


app = FastAPI(lifespan=lifespan)

# CORS configuration - restricted to safe origins
allowed_origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8000",
    "http://localhost:8080",
    "https://ai-fellows-project.onrender.com",
    os.getenv("FRONTEND_URL", ""),
]

# Remove empty strings
allowed_origins = [origin for origin in allowed_origins if origin]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Serve frontend static files
frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve SPA - fallback to index.html for all routes"""
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        # Return index.html for all routes (SPA routing)
        index_html = frontend_dist / "index.html"
        if index_html.exists():
            return FileResponse(index_html, media_type="text/html")
        return {"error": "Frontend not built. Run: cd frontend && npm run build"}
else:
    logger.warning(f"Frontend dist not found at {frontend_dist}. SPA routes will not be served.")
