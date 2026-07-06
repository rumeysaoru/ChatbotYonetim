from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: str | None = None
    working_unit_id: int