from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

class FeedbackCreate(BaseModel):
    text: str = Field(..., description="Raw text of the feedback")
    source: str = Field(..., description="Source channel (e.g. web, email, API, file)")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Numerical rating (1 to 5 stars)")
    metadata_json: Optional[Dict] = Field(default_factory=dict, description="Source-specific metadata")

class FeedbackUpdate(BaseModel):
    category: Optional[str] = None
    status: Optional[str] = None  # new, assigned, resolved
    assigned_to: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: int
    text: str
    cleaned_text: Optional[str] = None
    source: str
    rating: Optional[int] = None
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    category: str
    urgency_score: float
    is_urgent: bool
    is_trending: bool
    status: str
    assigned_to: Optional[str] = None
    created_at: datetime
    metadata_json: Optional[Dict] = None

    model_config = ConfigDict(from_attributes=True)

class InsightResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    impact_score: float
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class IntegrationConfigResponse(BaseModel):
    id: int
    name: str
    config_json: Dict
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class IntegrationUpdate(BaseModel):
    config_json: Dict
    is_active: bool

class DashboardMetrics(BaseModel):
    total_feedback: int
    average_rating: Optional[float] = None
    sentiment_distribution: Dict[str, int]
    category_distribution: Dict[str, int]
    urgency_count: int
    resolution_rate: float

class TrendPoint(BaseModel):
    date: str
    positive_count: int
    neutral_count: int
    negative_count: int
    avg_urgency: float
