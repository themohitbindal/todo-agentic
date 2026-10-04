"""HTTP layer for todos: URL + method -> function. Talks to crud, never to SQL directly."""

from fastapi import APIRouter, HTTPException, status

from app.crud import todo as crud
from app.database import DbSession
from app.schemas import TodoCreate, TodoRead, TodoUpdate

# Every route below is mounted under /todos and grouped as "todos" in /docs.
router = APIRouter(prefix="/todos", tags=["todos"])


def get_todo_or_404(db: DbSession, todo_id: int):
    todo = crud.get_todo(db, todo_id)
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo


@router.get("", response_model=list[TodoRead])
def list_todos(db: DbSession):
    return crud.list_todos(db)


@router.get("/{todo_id}", response_model=TodoRead)
def read_todo(todo_id: int, db: DbSession):
    return get_todo_or_404(db, todo_id)


@router.post("", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
def create_todo(data: TodoCreate, db: DbSession):
    return crud.create_todo(db, data)


@router.patch("/{todo_id}", response_model=TodoRead)
def update_todo(todo_id: int, data: TodoUpdate, db: DbSession):
    todo = get_todo_or_404(db, todo_id)
    return crud.update_todo(db, todo, data)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, db: DbSession):
    todo = get_todo_or_404(db, todo_id)
    crud.delete_todo(db, todo)
