from typing import Any, Optional, cast
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.crud.task import task as crud_task
from app.models.task import TaskCreate, TaskUpdate, TaskResponse, TaskPriority, TaskStatus
from app.models.database import User
from app.core.rate_limiter import rate_limiter_moderate, rate_limiter_strict
from app.core.cache import cache_manager
# from app.core.email import send_task_reminder_email

router = APIRouter()

@router.get("/")
async def read_tasks(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of tasks to return"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, min_length=1, description="Search in title and description"),
    current_user: User = Depends(deps.get_current_active_user),
    _: None = Depends(rate_limiter_strict),
) -> dict[str, Any]:
    """Retrieve tasks with advanced filtering and caching."""

    # Try cache first for common queries
    tasks, total_count = await crud_task.get_tasks_by_owner_cached(
        db,
        owner_id= cast(int, current_user.id),
        skip=skip,
        limit=limit,
        priority=priority,
        status=status,
        search=search
    )

    return {
        "tasks": tasks,
        "total": total_count,
        "page": (skip // limit) + 1,
        "pages": (total_count + limit - 1) // limit,
        "per_page": limit
    }

@router.get("/statistics")
async def get_task_statistics(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    _: None = Depends(rate_limiter_moderate),
) -> dict[str, int]:
    """Get task statistics for dashboard."""
    stats = await crud_task.get_task_statistics(db, owner_id=cast(int, current_user.id))
    return stats

@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    *,
    db: AsyncSession = Depends(deps.get_db),
    task_in: TaskCreate,
    # background_tasks: BackgroundTasks,
    current_user: User = Depends(deps.get_current_active_user),
    _: None = Depends(rate_limiter_strict),
) -> TaskResponse:
    """Create new task with background email notification."""

    task = await crud_task.create_with_owner(
        db, obj_in=task_in, owner_id=cast(int, current_user.id)
    )

    # Clear user's task cache
    await cache_manager.clear_pattern(f"tasks_by_owner:*:{current_user.id}:*")

    # Send background email notification if due date is set
    # if task.due_date:
    #     background_tasks.add_task(
    #         send_task_reminder_email,
    #         email_to=current_user.email,
    #         username=current_user.username,
    #         task_title=task.title,
    #         due_date=task.due_date.strftime("%Y-%m-%d %H:%M")
    #     )

    return task

@router.get("/{id}", response_model=TaskResponse)
async def read_task(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
    _: None = Depends(rate_limiter_moderate),
) -> TaskResponse:
    """Get task by ID with caching."""

    # Try cache first
    cache_key = f"task:{id}:{current_user.id}"
    cached_task = await cache_manager.get(cache_key)
    if cached_task:
        return cached_task

    task = await crud_task.get(db, id=id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if cast(int, task.owner_id) != cast(int, current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Cache the result with explicit type annotation
    task_dict: dict[str, Any] = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "status": task.status,
        "due_date": task.due_date,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "owner_id": task.owner_id
    }
    await cache_manager.set(cache_key, task_dict, ttl=600)  # 10 minutes

    return task

@router.put("/{id}", response_model=TaskResponse)
async def update_task(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    task_in: TaskUpdate,
    current_user: User = Depends(deps.get_current_active_user),
    _: None = Depends(rate_limiter_moderate),
) -> TaskResponse:
    """Update a task and invalidate cache."""

    task = await crud_task.get(db, id=id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if cast(int, task.owner_id) != cast(int, current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    task = await crud_task.update(db, db_obj=task, obj_in=task_in)

    # Invalidate caches
    await cache_manager.delete(f"task:{id}:{current_user.id}")
    await cache_manager.clear_pattern(f"tasks_by_owner:*:{current_user.id}:*")

    return task

@router.delete("/{id}")
async def delete_task(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
    _: None = Depends(rate_limiter_moderate),
) -> dict[str, str]:
    """Delete a task and clear cache."""

    task = await crud_task.get(db, id=id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if cast(int, task.owner_id) != cast(int, current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    await crud_task.remove(db, id=id)

    # Clear caches
    await cache_manager.delete(f"task:{id}:{current_user.id}")
    await cache_manager.clear_pattern(f"tasks_by_owner:*:{current_user.id}:*")

    return {"message": "Task deleted successfully"}
