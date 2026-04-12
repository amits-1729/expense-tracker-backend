from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

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