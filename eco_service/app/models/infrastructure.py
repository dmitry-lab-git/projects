from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class BagRead(BaseModel):
    bag_id: UUID
    resident_id: UUID
    yard_id: UUID
    type_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BagAllocationPayload(BaseModel):
    """Схема одной фракции внутри JSONB payload при BagSorted"""
    category_id: UUID
    weight_kg: float = Field(..., ge=0.0, description="Вес фракции в кг")


class BagEventPayload(BaseModel):
    """Свободный или структурированный контекст события"""
    weight_kg: Optional[float] = None
    allocations: Optional[List[BagAllocationPayload]] = None
    rejection_reason: Optional[str] = None


class BagEventCreate(BaseModel):
    bag_id: UUID
    event_type_id: UUID
    operator_id: Optional[UUID] = None
    payload: Dict[str, Any] = Field(default_factory=dict)


class BagEventRead(BaseModel):
    event_id: UUID
    bag_id: UUID
    event_type_id: UUID
    operator_id: Optional[UUID] = None
    payload: Dict[str, Any]
    occurred_at: datetime

    model_config = ConfigDict(from_attributes=True)