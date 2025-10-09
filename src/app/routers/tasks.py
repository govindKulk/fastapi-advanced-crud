from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Any

from app.models.task import (
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse,
    TaskPriority, TaskStatus
)

from app.core.exceptions import (
    TaskNotFoundError
)

router = APIRouter(prefix="/tasks", tags=["tasks"])

# Store as dictionaries for flexibility
tasks_db: List[dict[str, Any]] = []
next_id = 1

@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(task: TaskCreate) -> TaskResponse:
    """Create a new task with validation"""
    global next_id
    
    new_task: dict[str, Any] = {
        "id": next_id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "due_date": task.due_date,
        "status": TaskStatus.PENDING,
    }
    
    tasks_db.append(new_task)
    next_id += 1
    
    return TaskResponse(**new_task)

@router.get("/", response_model=TaskListResponse)
async def get_tasks(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, min_length=1, description="Search in title and description")
) -> TaskListResponse:
    """Get all tasks with filtering and pagination"""
    filtered_tasks = tasks_db.copy()

    if priority:
        filtered_tasks = [t for t in filtered_tasks if t["priority"] == priority]

    if status:
        filtered_tasks = [t for t in filtered_tasks if t["status"] == status]

    if search:
        search_lower = search.lower()
        filtered_tasks = [
            t for t in filtered_tasks
            if search_lower in t["title"].lower() or
               (t.get("description") and search_lower in t["description"].lower())
        ]

    total = len(filtered_tasks)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_tasks = filtered_tasks[start_idx:end_idx]

    return TaskListResponse(
        tasks=[TaskResponse(**t) for t in paginated_tasks],
        total=total,
        page=page,
        per_page=per_page
    )

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int) -> TaskResponse:
    """Get a specific task by ID"""
    task = next((t for t in tasks_db if t["id"] == task_id), None)
    if not task:
        raise TaskNotFoundError(task_id)
    return TaskResponse(**task)

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskUpdate) -> TaskResponse:
    """Update an existing task"""
    task_index = next((i for i, t in enumerate(tasks_db) if t["id"] == task_id), None)
    if task_index is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks_db[task_index]
    update_data = task_update.model_dump(exclude_unset=True)
    
    task.update(update_data)
    
    return TaskResponse(**task)

@router.delete("/{task_id}")
async def delete_task(task_id: int) -> dict[str, str]:
    """Delete a task"""
    global tasks_db
    task = next((t for t in tasks_db if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    tasks_db = [t for t in tasks_db if t["id"] != task_id]
    return {"message": f"Task '{task['title']}' deleted successfully"}
