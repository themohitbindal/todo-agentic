"""Pydantic schemas = the shape of JSON going IN to and OUT of the API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TodoBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None


class TodoCreate(TodoBase):
    """Body for POST /todos."""


class TodoUpdate(BaseModel):
    """Body for PATCH /todos/{id}. Every field optional: send only what changes."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    completed: bool | None = None


class TodoRead(TodoBase):
    """What the API sends back."""

    # Lets Pydantic read values from an ORM object's attributes (todo.title),
    # not only from a dict (todo["title"]).
    model_config = ConfigDict(from_attributes=True)

    id: int
    completed: bool
    created_at: datetime
    updated_at: datetime
