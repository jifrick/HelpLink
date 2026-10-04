from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.schemas.category import CategoryOut
from app.core.constants import ALLOWED_RESOURCE_TYPES
from app.services.utils import validate_url_string

class ResourceBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=20)
    category_id: int
    resource_type: str
    location: str = Field(default="Remote", max_length=150)
    url: str
    contact: Optional[str] = None
    tags: Optional[List[str]] = []

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        clean_url = v.strip()
        if not validate_url_string(clean_url):
            raise ValueError("URL must be a valid web address starting with http:// or https://")
        return clean_url

    @field_validator("resource_type")
    @classmethod
    def validate_resource_type(cls, v: str) -> str:
        clean_type = v.strip()
        if clean_type not in ALLOWED_RESOURCE_TYPES:
            raise ValueError(f"Resource type must be one of: {', '.join(ALLOWED_RESOURCE_TYPES)}")
        return clean_type

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

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        clean_url = v.strip()
        if not validate_url_string(clean_url):
            raise ValueError("URL must be a valid web address starting with http:// or https://")
        return clean_url

    @field_validator("resource_type")
    @classmethod
    def validate_resource_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        clean_type = v.strip()
        if clean_type not in ALLOWED_RESOURCE_TYPES:
            raise ValueError(f"Resource type must be one of: {', '.join(ALLOWED_RESOURCE_TYPES)}")
        return clean_type

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
