from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class ReportCreate(BaseModel):
    resource_id: int
    reason: str = Field(..., max_length=100) # broken_link, incorrect, spam, misleading, inappropriate, duplicate, other
    details: Optional[str] = None

class ReportOut(BaseModel):
    id: int
    resource_id: int
    user_id: Optional[int] = None
    reason: str
    details: Optional[str] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
