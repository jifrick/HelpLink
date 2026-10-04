from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.core.constants import ALLOWED_REPORT_REASONS

class ReportCreate(BaseModel):
    resource_id: int
    reason: str = Field(..., max_length=100)
    details: Optional[str] = None

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v: str) -> str:
        clean_reason = v.strip().lower()
        if clean_reason not in ALLOWED_REPORT_REASONS:
            raise ValueError(f"Report reason must be one of: {', '.join(ALLOWED_REPORT_REASONS)}")
        return clean_reason

class ReportOut(BaseModel):
    id: int
    resource_id: int
    user_id: Optional[int] = None
    reason: str
    details: Optional[str] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
