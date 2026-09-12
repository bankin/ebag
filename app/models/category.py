from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class Category(BaseModel):
    id: int
    name: str
    parent: Optional[Category] = None