import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app import models  # noqa: F401
from app.api.auth import router as auth_router
from app.api.routes import router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.base import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.6.0",
    description=(
        "Sistema de abertura, triagem e análise de chamados de TI "
        "com apoio de Inteligência Artificial. "
        "Projeto educacional para portfólio com foco em IA responsável."
    ),
    lifespan=lifespan,
)

origins = [
    origin.strip()
    for origin in settings.allowed_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(auth_router)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

setup_logging()

logger = logging.getLogger("helpdesk_ai")


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = time.perf_counter()

    response = await call_next(request)

    duration_ms = int((time.perf_counter() - start) * 1000)

    logger.info(
        f"request_id={request_id} "
        f"method={request.method} "
        f"path={request.url.path} "
        f"status_code={response.status_code} "
        f"duration_ms={duration_ms}"
    )

    response.headers["X-Request-ID"] = request_id

    return response


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/static/index.html")
