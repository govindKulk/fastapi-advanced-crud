from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from time import time

from app.api import deps
from typing import Any
from app.core.cache import cache_manager

router = APIRouter()

@router.get("/metrics", tags=["monitoring"])
async def get_metrics(
    db: AsyncSession = Depends(deps.get_db)
) -> Any:
    """Basic application metrics"""

    # Get task statistics
    result = await db.execute(text("""
        SELECT
            COUNT(*) as total_tasks,
            COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) as completed_tasks,
            COUNT(CASE WHEN created_at > NOW() - INTERVAL '24 hours' THEN 1 END) as tasks_created_today
        FROM tasks
    """))

    stats = result.first()

    return {
        "timestamp": time(),
        "tasks": {
            "total": stats.total_tasks if stats else 0,
            "completed": stats.completed_tasks if stats else 0,
            "created_today": stats.tasks_created_today if stats else 0
        }
    }

@router.get("/health", tags=["monitoring"])
async def health_check(
    db: AsyncSession | None = Depends(deps.get_db)
) -> dict[str, Any]:
    """Health check endpoint to verify Redis connection"""
    redis_connected = cache_manager.redis_client is not None
    cache_working = False
    if redis_connected:
        await cache_manager.set("health_check", "ok")
        if await cache_manager.get("health_check") != "ok":
            cache_working = False
        else:
            cache_working = True

    database_working = True
    if db is None:
        database_working = False
    else:
        try:
            await db.execute(text("SELECT 1"))
        except Exception:
            database_working = False

    
    return {
        "status": "healthy" if (redis_connected and database_working and cache_working) else "degraded",
        "redis_connected": redis_connected,
        "cache_enabled": redis_connected,
        "time": time(),
        "services": {
            "cache": "working" if cache_working else "not working",
            "redis": "connected" if redis_connected else "not connected",
            "database": "working" if database_working else "not working",
        }
    }
