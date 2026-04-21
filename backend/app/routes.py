from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func

from app.models import Task

router = APIRouter()


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: str = "medium"


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
    priority: str | None = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    completed: bool
    priority: str

    model_config = {"from_attributes": True}


class PaginatedTaskResponse(BaseModel):
    items: list[TaskResponse]
    total: int
    limit: int
    offset: int


@router.get("/tasks", response_model=PaginatedTaskResponse)
async def list_tasks(
    completed: Optional[bool] = None,
    priority: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    from app.main import app

    async with app.state.db_session() as session:
        # Build base query
        query = select(Task).order_by(Task.id)

        # Apply filters
        if completed is not None:
            query = query.where(Task.completed == completed)
        if priority is not None:
            query = query.where(Task.priority == priority)

        # Count total before pagination
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar()

        # Apply pagination
        query = query.offset(offset).limit(limit)
        result = await session.execute(query)
        items = result.scalars().all()

        return PaginatedTaskResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset
        )


@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(payload: TaskCreate):
    from app.main import app

    async with app.state.db_session() as session:
        task = Task(
            title=payload.title,
            description=payload.description,
            priority=payload.priority,
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int):
    from app.main import app

    async with app.state.db_session() as session:
        task = await session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, payload: TaskUpdate):
    from app.main import app

    async with app.state.db_session() as session:
        task = await session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(task, field, value)
        await session.commit()
        await session.refresh(task)
        return task


@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int):
    from app.main import app

    async with app.state.db_session() as session:
        task = await session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        await session.delete(task)
        await session.commit()
