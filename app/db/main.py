from sqlmodel import Session, create_engine

from app.db.schema import product, category

jdbc = 'postgresql://root:some@localhost:5432/ebag'
engine = create_engine(jdbc, pool_pre_ping=True, echo=True)

# def init_db() -> None:
#     SQLModel.metadata.create_all(engine)

# FIXME
def verify_migrations():
    return True
#     alembic_cfg = Config("alembic.ini")
#     current != head check


def get_session():
    with Session(engine) as session:
        yield session