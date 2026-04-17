from pydantic import BaseModel, EmailStr, Field

class RegisterUser(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=4)

class LoginUser(BaseModel):
    email: EmailStr
    password: str


class CategoryCreate(BaseModel):
    category: str
    id: int