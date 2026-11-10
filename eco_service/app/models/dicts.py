from uuid import UUID
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class YardBase(BaseModel):
    name: str = Field(..., max_length=150, description="Name of the community or collection yard point")
    address: Optional[str] = Field(None, description="Physical street address")
    location: Optional[Any] = Field(None, description="PostGIS GPS coordinates (Point)")
    is_active: bool = Field(True, description="Activity flag for collection logistics")


class YardRead(YardBase):
    yard_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BagEventTypeRead(BaseModel):
    event_type_id: UUID
    code: str = Field(..., max_length=50, description="String identifier code (e.g., BagSorted)")
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BagTypeRead(BaseModel):
    type_id: UUID
    code: str = Field(..., max_length=30, description="CLEAN_DRY, DIRTY_MIXED, ORGANIC")
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoryRead(BaseModel):
    category_id: UUID
    code: str = Field(..., max_length=30)
    name: str = Field(..., max_length=100)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OperatorBase(BaseModel):
    username: str = Field(..., max_length=50)
    full_name: str = Field(..., max_length=150)
    role: str = Field(..., max_length=30, description="COLLECTOR, SORTER, MANAGER, CEO")
    access_level: int = Field(..., ge=0, le=3, description="RBAC access level tier (0..3)")
    is_active: bool = True


class OperatorRead(OperatorBase):
    operator_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

