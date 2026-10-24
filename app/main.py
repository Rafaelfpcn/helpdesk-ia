from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app import models  # noqa: F401 (registra todas as tabelas no SQLAlchemy)
from app.config import settings
from app.database import Base, engine
from app.errors import AppError
from app.routers import metrics, pages, reviews, tickets

STATIC_DIR = Path(__file__).resolve().parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria as tabelas na inicialização se ainda não existirem.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    description="Triagem inteligente de chamados de TI com apoio de IA e supervisão humana obrigatória.",
    version="0.1.0",
    lifespan=lifespan,
)

# Servir arquivos estáticos (CSS e JS)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Tratamento padronizado de exceções de negócio
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


# Inclusão dos roteadores da API e das páginas web
app.include_router(tickets.router)
app.include_router(reviews.router)
app.include_router(metrics.router)
app.include_router(pages.router)


@app.get("/health", tags=["infra"])
def health():
    return {"status": "ok"}
