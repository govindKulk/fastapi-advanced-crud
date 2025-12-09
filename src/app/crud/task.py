from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import ColumnElement, select, func, or_, and_
from app.crud.base import CRUDBase
from app.models.database import Task
from app.models.task import TaskCreate, TaskUpdate, TaskPriority, TaskStatus
from app.core.decorators import cache_result

class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    @cache_result(ttl=300, key_prefix="tasks_by_owner")
    async def get_tasks_by_owner_cached(
        self,
        db: AsyncSession,
        *,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
        priority: Optional[TaskPriority] = None,
        status: Optional[TaskStatus] = None,
        search: Optional[str] = None
    ) -> tuple[list[dict[str, str | int | datetime]], int]:
        """Get tasks with caching and full-text search"""

        # Build base query with eager loading
        query = select(Task).where(Task.owner_id == owner_id)
        count_query = select(func.count(Task.id)).where(Task.owner_id == owner_id)

        # Apply filters
        conditions : list[ColumnElement[bool]] = [] 
        if priority:
            conditions.append(Task.priority == priority)
        if status:
            conditions.append(Task.status == status)
        if search:
            search_condition = or_(
                Task.title.ilike(f"%{search}%"),
                Task.description.ilike(f"%{search}%")
            )
            conditions.append(search_condition)

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        # Execute count query
        count_result = await db.execute(count_query)
        total_count : int = count_result.scalar() or 0

        # Execute main query with pagination
        query = query.offset(skip).limit(limit).order_by(Task.created_at.desc())
        result = await db.execute(query)
        tasks = result.scalars().all()
    
        # Convert to dict for caching
        task_dicts : list[dict[str, str | int | datetime]] = [
            {
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
            for task in tasks
        ] # type: ignore[var-annotated]

        return task_dicts, total_count


    async def create_with_owner(
        self, db: AsyncSession, *, obj_in: TaskCreate, owner_id: int
    ) -> Task:
        obj_in_data = obj_in.model_dump()
        db_obj = Task(**obj_in_data, owner_id=owner_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_task_statistics(
        self, db: AsyncSession, *, owner_id: int
    ) -> dict[str, int]:
        """Get task statistics for dashboard"""
        query = select(
            func.count(Task.id).label("total_tasks"),
            func.sum(func.case((Task.status == TaskStatus.COMPLETED, 1), else_=0)).label("completed_tasks"),
            func.sum(func.case((Task.status == TaskStatus.PENDING, 1), else_=0)).label("pending_tasks"),
            func.sum(func.case((Task.status == TaskStatus.IN_PROGRESS, 1), else_=0)).label("in_progress_tasks"),
            func.sum(func.case((Task.priority == TaskPriority.HIGH, 1), else_=0)).label("high_priority_tasks"),
            func.sum(func.case((Task.priority == TaskPriority.URGENT, 1), else_=0)).label("urgent_tasks"),
        ).where(Task.owner_id == owner_id)

        result = await db.execute(query)
    
        stats = result.first()

        if stats is None:
            return {
                "total_tasks": 0,
                "completed_tasks": 0,
                "pending_tasks": 0,
                "in_progress_tasks": 0,
                "high_priority_tasks": 0,
                "urgent_tasks": 0,
            }
        

        
        return {
            "total_tasks": stats.total_tasks or 0,
            "completed_tasks": stats.completed_tasks or 0,
            "pending_tasks": stats.pending_tasks or 0,
            "in_progress_tasks": stats.in_progress_tasks or 0,
            "high_priority_tasks": stats.high_priority_tasks or 0,
            "urgent_tasks": stats.urgent_tasks or 0,
        }


task = CRUDTask(Task)