from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.routes import deals_router, exports_router, lots_router, matches_router
from app.core.config import settings
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    yield


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(lots_router)
app.include_router(matches_router)
app.include_router(deals_router)
app.include_router(exports_router)


@app.get("/health")
async def healthcheck() -> JSONResponse:
    return JSONResponse(
        content={
            "status": "ok",
            "app": settings.app_name,
            "env": settings.app_env,
            "provider_mode": settings.provider_mode,
        }
    )