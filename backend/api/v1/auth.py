from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from api.deps import get_current_user, get_user_service
from schemas.token import TokenRequestForm, Token
from schemas.users import UserCreate, UserOut
from services.users import UserService
from db.models.users import User

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

@router.post("/register", response_model=UserOut, status_code=201)
async def register_user(user_in: UserCreate, service: UserService = Depends(get_user_service)) -> UserOut:
    return await service.register(user_in)

@router.post("/token", response_model=Token, status_code=201)
async def token(form_data: TokenRequestForm = Depends(), service: UserService = Depends(get_user_service)) -> Token:
    if form_data.grant_type == "password":
        return await service.authenticate(form_data.email, form_data.password)
    elif form_data.grant_type == "refresh_token":
        return await service.refresh_token(form_data.refresh_token)
    raise HTTPException(status_code=400, detail="Invalid grant_type")

@router.post("/logout", status_code=204)
async def logout(token: Annotated[str, Depends(oauth2_scheme)], service: UserService = Depends(get_user_service)):
    await service.logout(token)

@router.get("/me", response_model=UserOut)
async def read_me(current_user: Annotated[User, Depends(get_current_user)]) -> UserOut:
    return current_user
