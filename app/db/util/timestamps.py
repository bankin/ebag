from datetime import UTC, datetime

import sqlalchemy as sa
from sqlmodel import Field, SQLModel


class TimestampedModel(SQLModel):
    created_at: datetime | None = Field(
        default=None,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={"server_default": sa.func.now()},
        nullable=False,
    )
    updated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(UTC),
        },
        sa_type=sa.TIMESTAMP(timezone=True),
    )
