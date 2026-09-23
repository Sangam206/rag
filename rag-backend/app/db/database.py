from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()


def init_db():
    import app.db.models
    Base.metadata.create_all(bind=engine)
