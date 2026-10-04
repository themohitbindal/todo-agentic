"""CRUD functions = all database work for todos. No HTTP stuff in here."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Todo
from app.schemas import TodoCreate, TodoUpdate


def list_todos(db: Session) -> list[Todo]:
    return list(db.scalars(select(Todo).order_by(Todo.id)))


def get_todo(db: Session, todo_id: int) -> Todo | None:
    return db.get(Todo, todo_id)


def create_todo(db: Session, data: TodoCreate) -> Todo:
    todo = Todo(**data.model_dump())
    db.add(todo)
    db.commit()
    db.refresh(todo)  # reload DB-generated values (id, created_at, ...)
    return todo


def update_todo(db: Session, todo: Todo, data: TodoUpdate) -> Todo:
    # exclude_unset=True -> only the fields the client actually sent.
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(todo, field, value)
    db.commit()
    db.refresh(todo)
    return todo


def delete_todo(db: Session, todo: Todo) -> None:
    db.delete(todo)
    db.commit()
