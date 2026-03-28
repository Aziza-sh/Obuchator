from typing import Optional

from fastapi import Form
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class TokenRequestForm:
    def __init__(
        self,
        grant_type: str = Form(..., pattern="password|refresh_token"),
        email: Optional[str] = Form(None),
        password: Optional[str] = Form(None),
        refresh_token: Optional[str] = Form(None),
    ):
        self.grant_type = grant_type
        self.email = email
        self.password = password
        self.refresh_token = refresh_token
