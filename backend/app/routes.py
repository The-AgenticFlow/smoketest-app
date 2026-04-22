
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, field_validator
from sqlalchemy import func, select

from app.cache import cache
from app.models import Task
from app.sanitization import strip_html

router = APIRouter()

CACHE_KEY_TASKS_ALL = "tasks:all"


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: str = "medium"
    completed: bool = False

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Strip HTML, check for empty, check max length."""
        if v is None:
            raise ValueError('title cannot be None')

        # Strip HTML tags
        cleaned = strip_html(v)

        # Strip whitespace
        cleaned = cleaned.strip()

        # Check for empty title
        if not cleaned:
            raise ValueError('title cannot be empty')

        # Check max length (255 characters)
        if len(cleaned) > 255:
            raise ValueError('title cannot exceed 255 characters')

        return cleaned

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        """Strip HTML tags from description."""
        if v is None:
            return v

        # Strip HTML tags
        cleaned = strip_html(v)

        return cleaned


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
    priority: str | None = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Strip HTML, check for empty, check max length."""
        if v is None:
            return v

        # Strip HTML tags
        cleaned = strip_html(v)

        # Strip whitespace
        cleaned = cleaned.strip()

        # Check for empty title
        if not cleaned:
            raise ValueError('title cannot be empty')

        # Check max length (255 characters)
        if len(cleaned) > 255:
            raise ValueError('title cannot exceed 255 characters')

        return cleaned

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        """Strip HTML tags from description."""
        if v is None:
            return v

        # Strip HTML tags
        cleaned = strip_html(v)

        return cleaned


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
    completed: bool | None = None,
    priority: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    from app.main import app

    # Build cache key based on filter parameters
    cache_key = f"{CACHE_KEY_TASKS_ALL}:{completed}:{priority}:{limit}:{offset}"

    # Check cache first
    cached = await cache.get(cache_key)
    if cached is not None:
        # Return cached data directly
        return PaginatedTaskResponse(**cached)

    # Cache miss - fetch from database
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

        response = PaginatedTaskResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset
        )

        # Cache the response
        await cache.set(cache_key, response.model_dump(), ttl=300)
        return response


@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(payload: TaskCreate):
    from app.main import app

    async with app.state.db_session() as session:
        task = Task(
            title=payload.title,
            description=payload.description,
            priority=payload.priority,
            completed=payload.completed,
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
        return None
