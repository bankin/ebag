from sqlmodel import Session, create_engine, SQLModel

from app.db.schema import product, category

jdbc = 'postgresql://root:some@localhost:5432/ebag'
engine = create_engine(jdbc, pool_pre_ping=True, echo=True)

def init_db() -> None:
    SQLModel.metadata.create_all(engine)