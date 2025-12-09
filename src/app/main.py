from contextlib import asynccontextmanager
from fastapi import FastAPI,  HTTPException, status
from app.routers import tasks, auth, files
from app.core.cache import cache_manager
from pydantic import BaseModel
from typing import List, cast
import logging
import sys

# Configure logging at application startup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize resources
    logger.info("Starting up application...")
    app.state.messages = cast(List[str], [])
    
    # Connect to Redis
    await cache_manager.connect()
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown: Cleanup resources
    logger.info("Shutting down application...")
    app.state.messages.clear()
    
    # Disconnect from Redis
    await cache_manager.disconnect()
    logger.info("Application shutdown complete")


task_app = FastAPI(
    title="Task Management API",
    description="A simple Task Management API built with FastAPI",
    version="1.0.0",
    lifespan=lifespan,
)

task_app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
task_app.include_router(auth.router, prefix="/auth", tags=["auth"])
task_app.include_router(files.router, tags=["files"])


@task_app.get("/health")
async def health_check() -> dict[str, str | bool]:
    """Health check endpoint to verify Redis connection"""
    redis_connected = cache_manager.redis_client is not None
    
    return {
        "status": "healthy" if redis_connected else "degraded",
        "redis_connected": redis_connected,
        "cache_enabled": redis_connected
    }

@task_app.get("/messages")
async def get_messages() -> List[str]:
    return task_app.state.messages

@task_app.post("/messages")
async def add_message(message: str) -> dict[str, str]:
    task_app.state.messages.append(message)
    return {"message": "Message added successfully"}

class RootResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str

@task_app.get(
    "/",
    response_model=RootResponse,
    responses={500: {"model": ErrorResponse, "description": "Internal Server Error"},
               200: {"model": RootResponse, "description": "Successful Response", "name": "govind"}},
    tags=["root"],
)
def read_root() -> RootResponse:
    try:
        return RootResponse(message="Welcome to the Task Management API!")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(task_app, host="0.0.0.0", port=8000)
