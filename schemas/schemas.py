from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional


class RegisterUser(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=4)


class LoginUser(BaseModel):
    email: EmailStr
    password: str


class CategoryCreate(BaseModel):
    category: str


class CategoryDelete(BaseModel):
    id: int


class AddExpense(BaseModel):
    category_id: int
    amount: float = Field(..., gt=0)
    description: Optional[str] = None
    expense_date: date
    payment_method: str = Field(..., min_length=2, max_length=50)


class UpdateExpense(BaseModel):
    category_id: Optional[int] = None
    amount: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None
    expense_date: Optional[date] = None
    payment_method: Optional[str] = Field(None, min_length=2, max_length=50)