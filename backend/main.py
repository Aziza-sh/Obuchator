import asyncio
import logging
import traceback
from contextlib import asynccontextmanager

from api.v1.auth import router as auth_router
from api.v1.courses import router as courses_router
from api.v1.metrics import router as metrics_router
from api.v1.news import router as news_router
from api.v1.news_subscription import router as news_sub_router
from api.v1.telegram import router as telegram_router
from api.v1.ws import router as ws_router
from core.config import settings
from core.exceptions import (
    CredentialsException,
    MetricsException,
    NewsNotFoundException,
)
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jose.exceptions import JWTError
from starlette.exceptions import HTTPException as StarletteHTTPException

templates = Jinja2Templates(directory="templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.TELEGRAM_BOT_TOKEN:
        from db.session import async_session_local
        from redis.asyncio import Redis
        from services.telegram_bot import start_polling

        redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        await start_polling(redis, async_session_local)
        logging.info("Telegram bot started")

    yield

    if settings.TELEGRAM_BOT_TOKEN:
        from services.telegram_bot import stop_polling
        await stop_polling()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="frontend/static", html=True), name="static")


@app.exception_handler(JWTError)
async def jwt_handler(request: Request, exc: JWTError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": "Invalid or revoked token"})


@app.exception_handler(CredentialsException)
async def credentials_handler(
    request: Request, exc: CredentialsException
) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc)})


@app.exception_handler(RequestValidationError)
async def validation_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(NewsNotFoundException)
async def news_not_found_handler(request: Request, exc: NewsNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"detail": f"News with id {exc.news_id} not found"},
    )


@app.exception_handler(MetricsException)
async def metrics_error_handler(request: Request, exc: MetricsException):
    return JSONResponse(status_code=500, content={"detail": "Metrics service error"})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(traceback.format_exc())
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("main_page.html", {"request": request})


app.include_router(auth_router)
app.include_router(news_sub_router)
app.include_router(news_router)
app.include_router(courses_router)
app.include_router(ws_router)
app.include_router(metrics_router)
app.include_router(telegram_router)
