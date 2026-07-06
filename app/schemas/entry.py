"""
Veri girişi formu için doğrulama şeması.
"""

from pydantic import BaseModel, Field

class EntryCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)