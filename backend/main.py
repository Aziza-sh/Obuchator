from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from jose.exceptions import JWTError

from fastapi.staticfiles import StaticFiles
from core.exceptions import CredentialsException
from api.v1.auth import router as auth_router
app = FastAPI()

app.mount("/static", StaticFiles(directory="static", html=True), name="static")

@app.exception_handler(JWTError)
async def jwt_handler(request: Request, exc: JWTError) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={"detail": "Invalid or revoked token"}
    )
@app.exception_handler(CredentialsException)
async def credentials_handler(request: Request, exc: CredentialsException) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={"detail": str(exc)}
    )

@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "path": str(request.url)}
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "path": str(request.url)}
    )

app.include_router(auth_router)
