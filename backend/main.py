import logging
import traceback

from api.v1.auth import router as auth_router
from api.v1.metrics import router as metrics_router
from api.v1.news import router as news_router
from api.v1.ws import router as ws_router
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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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
    return JSONResponse(
        status_code=422, content={"detail": exc.errors(), "path": str(request.url)}
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "path": str(request.url)},
    )


@app.exception_handler(NewsNotFoundException)
async def news_not_found_handler(request: Request, exc: NewsNotFoundException):

    return JSONResponse(
        status_code=404,
        content={
            "detail": f"News with id {exc.news_id} not found",
            "path": str(request.url),
        },
    )


@app.exception_handler(MetricsException)
async def metrics_error_handler(request: Request, exc: MetricsException):

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Metrics service error",
            "path": str(request.url),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):

    logging.error(traceback.format_exc())

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "path": str(request.url),
        },
    )


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("main_page.html", {"request": request})


app.include_router(auth_router)
app.include_router(news_router)
app.include_router(ws_router)
app.include_router(metrics_router)
