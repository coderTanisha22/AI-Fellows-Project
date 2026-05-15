from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .api.router import router
from .services.gemini_client import log_gemini_startup_status
from .services.simulator import simulator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Intelligent Care Assistant backend")
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

# CORS configuration - allow all origins for demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
            return {"file": str(file_path)}
        # Return index.html for all routes (SPA routing)
        index_html = frontend_dist / "index.html"
        if index_html.exists():
            return {"file": str(index_html)}
        return {"error": "Frontend not built. Run: cd frontend && npm run build"}
