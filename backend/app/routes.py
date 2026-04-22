from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.cache import cache
from app.models import Task

router = APIRouter()

CACHE_KEY_TASKS_ALL = "tasks:all"


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


@router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks():
    from app.main import app

    # Check cache first
    cached = await cache.get(CACHE_KEY_TASKS_ALL)
    if cached is not None:
        # Return cached data directly
        return cached

    # Cache miss - fetch from database
    async with app.state.db_session() as session:
        result = await session.execute(select(Task).order_by(Task.id))
        tasks = result.scalars().all()
        task_list = [TaskResponse.model_validate(t).model_dump() for t in tasks]
        await cache.set(CACHE_KEY_TASKS_ALL, task_list, ttl=300)
        return task_list


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
        # Invalidate cache after creating task
        await cache.delete(CACHE_KEY_TASKS_ALL)
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
        # Invalidate cache after updating task
        await cache.delete(CACHE_KEY_TASKS_ALL)
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
        # Invalidate cache after deleting task
        await cache.delete(CACHE_KEY_TASKS_ALL)
