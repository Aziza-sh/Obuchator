from pydantic import BaseModel, EmailStr
from uuid import UUID  

class BaseUser(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str

class UserCreate(BaseUser):
    password: str

class UserOut(BaseUser):
    is_admin: bool
    id: UUID