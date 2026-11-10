from uuid import UUID
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class KPISummaryDTO(BaseModel):
    total_mass_kg: float = 0.0
    total_bags_count: int = 0
    active_yards_count: int = 0
    active_operators_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class DailyTrendDTO(BaseModel):
    trend_date: date
    organic_kg: float = 0.0
    clean_dry_kg: float = 0.0
    dirty_mixed_kg: float = 0.0
    total_bags: int = 0

    model_config = ConfigDict(from_attributes=True)


class WasteByCategoryDTO(BaseModel):
    category_code: str
    category_name: str
    total_weight_kg: float
    percentage: float

    model_config = ConfigDict(from_attributes=True)


class YardPerformanceDTO(BaseModel):
    yard_id: UUID
    yard_name: str
    total_weight_kg: float
    bags_count: int
    last_collection_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class OperatorPerformanceDTO(BaseModel):
    operator_id: UUID
    full_name: str
    role: str
    events_count: int
    total_sorted_kg: float

    model_config = ConfigDict(from_attributes=True)