from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# check_same_thread=False é necessário no SQLite porque o FastAPI pode usar
# threads diferentes numa mesma requisição.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Classe base declarativa de todos os modelos (tabelas)."""
    pass


def get_db():
    """Dependência do FastAPI: abre uma sessão por requisição e sempre fecha no final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
