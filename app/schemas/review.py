from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.enums import Category, Priority


class ReviewConfirm(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    reviewed_by: str = Field(min_length=2, max_length=100, examples=["Carlos Atendente Teste"])
    note: Optional[str] = Field(default=None, max_length=500)


class ReviewChange(ReviewConfirm):
    category: Category
    priority: Priority
