from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

class Task(BaseModel):
    id: int
    title: str
    description: str = ""
    completed: bool = False

router = APIRouter(prefix="/tasks", tags=["tasks"])

# Use dict for O(1) lookups by ID
tasks_db: dict[int, Task] = {}
next_id: int = 0

@router.get("/", response_model=list[Task])
async def get_tasks() -> list[Task]:
    """Get all tasks"""
    return list(tasks_db.values())

@router.get("/{task_id}", response_model=Task)
async def get_task(task_id: int) -> Task:
    """Get a specific task by ID"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks_db[task_id]

@router.post("/", response_model=Task)
async def create_task(task: Task) -> Task:
    """Create a new task"""
    global next_id
    new_task = Task(id=next_id, **task.model_dump(exclude={"id"}))
    tasks_db[next_id] = new_task
    next_id += 1
    return new_task

@router.put("/{task_id}", response_model=Task)
async def update_task(task_id: int, updated_task: Task) -> Task:
    """Update an existing task"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    # Update the task, preserving ID
    tasks_db[task_id] = Task(id=task_id, **updated_task.model_dump(exclude={"id"}))
    return tasks_db[task_id]

@router.delete("/{task_id}")
async def delete_task(task_id: int) -> dict[str, str]:
    """Delete a task"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks_db[task_id]
    return {"message": "Task deleted"}