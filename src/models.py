from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON
from .database import Base

class FeedbackItem(Base):
    __tablename__ = "feedback_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    text = Column(Text, nullable=False)
    cleaned_text = Column(Text, nullable=True)
    source = Column(String(50), nullable=False)  # web, email, API, file
    rating = Column(Integer, nullable=True)
    sentiment_score = Column(Float, nullable=True)  # -1.0 to 1.0
    sentiment_label = Column(String(20), nullable=True)  # positive, neutral, negative
    category = Column(String(50), default="General")
    urgency_score = Column(Float, default=0.0)  # 0.0 to 100.0
    is_urgent = Column(Boolean, default=False)
    is_trending = Column(Boolean, default=False)
    status = Column(String(20), default="new")  # new, assigned, resolved
    assigned_to = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(JSON, nullable=True)  # flexible source-specific metadata (e.g. email sender, client ip)

class Insight(Base):
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    impact_score = Column(Float, default=0.0)  # 0.0 to 100.0
    status = Column(String(20), default="active")  # active, implemented, archived
    created_at = Column(DateTime, default=datetime.utcnow)

class IntegrationConfig(Base):
    __tablename__ = "integration_configs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)  # slack, teams, jira, salesforce
    config_json = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=False)
