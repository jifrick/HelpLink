from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.schemas.category import CategoryOut

class ResourceBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=20)
    category_id: int
    resource_type: str  # Opportunity, Course, Scholarship, Job, Internship, Event, Support, Tool, Other
    location: str = Field(default="Remote", max_length=150)
    url: str
    contact: Optional[str] = None
    tags: Optional[List[str]] = []

class ResourceCreate(ResourceBase):
    pass

class ResourceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    resource_type: Optional[str] = None
    location: Optional[str] = None
    url: Optional[str] = None
    contact: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None

class ResourceOut(BaseModel):
    id: int
    title: str
    slug: str
    description: str
    category_id: int
    resource_type: str
    location: str
    url: str
    contact: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryOut] = None
    tags: List[str] = []
    saved_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

    @field_validator("tags", mode="before")
    @classmethod
    def convert_tags(cls, v: Any) -> List[str]:
        if isinstance(v, list):
            return [item.name if hasattr(item, "name") else str(item) for item in v]
        return []

class ResourceListResponse(BaseModel):
    items: List[ResourceOut]
    total: int
    page: int
    pages: int
