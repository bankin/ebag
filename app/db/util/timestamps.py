from datetime import datetime, timezone

import sqlalchemy as sa
from sqlmodel import Field, SQLModel

class TimestampedModel(SQLModel):
    created_on: datetime | None = Field(
        default=None,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={"server_default": sa.func.now()},
        nullable=False,
    )
    updated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(timezone.utc),
        },
        sa_type=sa.TIMESTAMP(timezone=True),
    )