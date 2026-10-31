import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.database.init_db import init_database
from app.services.expiry_service import expiry_background_task
from app.api.auth import router as auth_router
from app.api.donations import router as donations_router
from app.api.requests import router as requests_router
from app.api.volunteer import router as volunteer_router
from app.api.notifications import router as notifications_router
from app.api.dashboard import router as dashboard_router
from app.api.ai import router as ai_router

background_tasks = set()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database & tables exist
    print("[CommunityFoodRescue] Initializing database and verifying schema...")
    init_database()

    # Start periodic background expiry watcher
    task = asyncio.create_task(expiry_background_task(interval_seconds=60))
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)
    print("[CommunityFoodRescue] Background expiry task started.")

    yield

    # Shutdown: cancel background tasks
    for t in background_tasks:
        t.cancel()
    print("[CommunityFoodRescue] Shutdown complete.")

app = FastAPI(
    title="Community Food Rescue Network API",
    description="Backend API connecting food donors, NGOs, and volunteers for surplus food redistribution.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(auth_router, prefix="/api")
app.include_router(donations_router, prefix="/api")
app.include_router(requests_router, prefix="/api")
app.include_router(volunteer_router, prefix="/api")
app.include_router(notifications_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(ai_router, prefix="/api")

# Static uploads directory for food photos
uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "Community Food Rescue Network",
        "database": "connected",
        "version": "1.0.0",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)

