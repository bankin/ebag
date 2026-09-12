from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class BaseCategory(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class CategoryRead(BaseCategory):
    model_config = ConfigDict(from_attributes=True)

    parent: BaseCategory | None = None


class CategoryCreate(BaseModel):
    name: str
    parent_id: int | None = None


class CategoryUpdate(BaseModel):
    name: str | None = None
    parent_id: int | None = None
