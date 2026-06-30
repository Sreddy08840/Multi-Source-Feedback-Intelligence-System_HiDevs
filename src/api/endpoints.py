import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.database import get_db
from src.models import FeedbackItem, Insight, IntegrationConfig
from src.schemas import (
    FeedbackCreate, FeedbackResponse, FeedbackUpdate, 
    DashboardMetrics, TrendPoint, IntegrationConfigResponse, IntegrationUpdate
)
from src.ingestion.webhooks import parse_webhook_payload
from src.ingestion.api_clients import AppStoreClient, GooglePlayClient, G2Client
from src.ingestion.file_importer import parse_csv_file
from src.processing.cleaner import clean_text
from src.processing.analyzer import SentimentAnalyzer
from src.processing.categorizer import FeedbackCategorizer
from src.processing.priority_scorer import calculate_priority
from src.intelligence.ml_models import MLClassifier
from src.intelligence.ai_prompts import AIIntelligenceEngine
from src.intelligence.trend_detector import TrendDetector
from src.actions.alerts import trigger_urgency_alert
from src.actions.integrations import create_jira_ticket, sync_to_salesforce
from src.actions.reports import generate_csv_report, generate_html_report

router = APIRouter()

# Singletons/instances for processing
categorizer = FeedbackCategorizer()
ai_engine = AIIntelligenceEngine()
trend_detector = TrendDetector()

async def process_and_save_feedback(db: Session, text: str, source: str, rating: Optional[int], metadata_json: Dict) -> FeedbackItem:
    """Helper to run a raw feedback item through the entire intelligence pipeline."""
    # 1. Clean
    cleaned = clean_text(text)

    # 2. Analyze Sentiment
    sentiment_score, sentiment_label = await SentimentAnalyzer.analyze(cleaned)

    # 3. Categorize (ML Classifier with keyword fallback)
    category = categorizer.categorize(cleaned)

    # 4. Priority Scorer
    urgency_score, is_urgent = calculate_priority(
        cleaned, sentiment_score, category, rating, metadata_json
    )

    # 5. Create database record
    db_item = FeedbackItem(
        text=text,
        cleaned_text=cleaned,
        source=source,
        rating=rating,
        sentiment_score=sentiment_score,
        sentiment_label=sentiment_label,
        category=category,
        urgency_score=urgency_score,
        is_urgent=is_urgent,
        status="new",
        metadata_json=metadata_json
    )
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    # 6. Trigger Alerts
    trigger_urgency_alert(db, db_item)

    # 7. Automated Workflows (e.g. Automatically create Jira Ticket if Bug and Urgent)
    if db_item.is_urgent and db_item.category == "Bug":
        create_jira_ticket(db, db_item)

    return db_item

@router.post("/feedback/ingest", response_model=FeedbackResponse)
async def ingest_feedback(payload: FeedbackCreate, db: Session = Depends(get_db)):
    """Unified webhook-ready endpoint for single feedback ingestion."""
    if not payload.text:
        raise HTTPException(status_code=400, detail="Feedback text cannot be empty.")
    
    # Check if this is a standard webhook or parsed payload
    if payload.source == "web":
        # Form submission simulation
        normalized = parse_webhook_payload(payload.model_dump())
        item = await process_and_save_feedback(
            db, 
            text=normalized["text"],
            source=normalized["source"],
            rating=normalized["rating"],
            metadata_json=normalized["metadata_json"]
        )
    else:
        # Standard API schema
        item = await process_and_save_feedback(
            db,
            text=payload.text,
            source=payload.source,
            rating=payload.rating,
            metadata_json=payload.metadata_json
        )
    return item

@router.post("/feedback/upload")
async def upload_csv_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Ingests a CSV file containing batch customer feedback."""
    contents = await file.read()
    items = parse_csv_file(contents)
    
    if not items:
        raise HTTPException(status_code=400, detail="No valid feedback items found in the CSV.")

    inserted_count = 0
    for data in items:
        await process_and_save_feedback(
            db,
            text=data["text"],
            source=data["source"],
            rating=data["rating"],
            metadata_json=data["metadata_json"]
        )
        inserted_count += 1
        
    return {"success": True, "count": inserted_count}

@router.get("/feedback", response_model=Dict[str, Any])
def list_feedback(
    source: Optional[str] = None,
    category: Optional[str] = None,
    sentiment_label: Optional[str] = None,
    status: Optional[str] = None,
    is_urgent: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Lists feedback items with search parameters and pagination filters."""
    query = db.query(FeedbackItem)

    if source:
        query = query.filter(FeedbackItem.source == source)
    if category:
        query = query.filter(FeedbackItem.category == category)
    if sentiment_label:
        query = query.filter(FeedbackItem.sentiment_label == sentiment_label)
    if status:
        query = query.filter(FeedbackItem.status == status)
    if is_urgent is not None:
        query = query.filter(FeedbackItem.is_urgent == is_urgent)
    if search:
        query = query.filter(
            FeedbackItem.text.ilike(f"%{search}%") | 
            FeedbackItem.category.ilike(f"%{search}%")
        )

    total = query.count()
    offset = (page - 1) * limit
    items = query.order_by(FeedbackItem.created_at.desc()).offset(offset).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "items": items
    }

@router.patch("/feedback/{item_id}", response_model=FeedbackResponse)
def update_feedback(item_id: int, payload: FeedbackUpdate, db: Session = Depends(get_db)):
    """Updates category, assignee, and status coordinates of feedback."""
    db_item = db.query(FeedbackItem).filter(FeedbackItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Feedback not found")

    if payload.category is not None:
        db_item.category = payload.category
    if payload.status is not None:
        db_item.status = payload.status
    if payload.assigned_to is not None:
        db_item.assigned_to = payload.assigned_to

    db.commit()
    db.refresh(db_item)
    return db_item

@router.post("/feedback/{item_id}/jira")
def trigger_manual_jira(item_id: int, db: Session = Depends(get_db)):
    """Manually creates a Jira issue ticket for a feedback item."""
    db_item = db.query(FeedbackItem).filter(FeedbackItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    result = create_jira_ticket(db, db_item)
    return result

@router.post("/feedback/{item_id}/salesforce")
def trigger_manual_salesforce(item_id: int, db: Session = Depends(get_db)):
    """Manually creates a Salesforce CRM lead/contact sync for a feedback item."""
    db_item = db.query(FeedbackItem).filter(FeedbackItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    result = sync_to_salesforce(db, db_item)
    return result

@router.get("/dashboard/metrics", response_model=DashboardMetrics)
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """Fetches high-level metrics for dashboard cards."""
    total_feedback = db.query(FeedbackItem).count()
    if total_feedback == 0:
        return DashboardMetrics(
            total_feedback=0,
            average_rating=0.0,
            sentiment_distribution={"positive": 0, "neutral": 0, "negative": 0},
            category_distribution={},
            urgency_count=0,
            resolution_rate=0.0
        )

    # Average rating
    avg_rating = db.query(func.avg(FeedbackItem.rating)).filter(FeedbackItem.rating != None).scalar() or 0.0

    # Sentiment distribution
    sentiment_rows = db.query(FeedbackItem.sentiment_label, func.count(FeedbackItem.id)).group_by(FeedbackItem.sentiment_label).all()
    sentiment_distribution = {"positive": 0, "neutral": 0, "negative": 0}
    for label, count in sentiment_rows:
        if label:
            sentiment_distribution[label] = count

    # Category distribution
    category_rows = db.query(FeedbackItem.category, func.count(FeedbackItem.id)).group_by(FeedbackItem.category).all()
    category_distribution = {cat: count for cat, count in category_rows if cat}

    # Urgency count (is_urgent = True and status != resolved)
    urgency_count = db.query(FeedbackItem).filter(
        FeedbackItem.is_urgent == True,
        FeedbackItem.status != "resolved"
    ).count()

    # Resolution rate
    resolved_count = db.query(FeedbackItem).filter(FeedbackItem.status == "resolved").count()
    resolution_rate = round((resolved_count / total_feedback) * 100, 1)

    return DashboardMetrics(
        total_feedback=total_feedback,
        average_rating=round(float(avg_rating), 1),
        sentiment_distribution=sentiment_distribution,
        category_distribution=category_distribution,
        urgency_count=urgency_count,
        resolution_rate=resolution_rate
    )

@router.get("/dashboard/trends", response_model=List[TrendPoint])
def get_dashboard_trends(days: int = 7, db: Session = Depends(get_db)):
    """Retrieves sentiment distribution and average urgency trends over past days."""
    trend_data = []
    now = datetime.utcnow()
    
    # Query database and group by date
    for i in range(days - 1, -1, -1):
        target_date = now - timedelta(days=i)
        start_dt = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0)
        end_dt = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59)

        pos_count = db.query(FeedbackItem).filter(FeedbackItem.created_at.between(start_dt, end_dt), FeedbackItem.sentiment_label == "positive").count()
        neu_count = db.query(FeedbackItem).filter(FeedbackItem.created_at.between(start_dt, end_dt), FeedbackItem.sentiment_label == "neutral").count()
        neg_count = db.query(FeedbackItem).filter(FeedbackItem.created_at.between(start_dt, end_dt), FeedbackItem.sentiment_label == "negative").count()
        
        avg_urgency = db.query(func.avg(FeedbackItem.urgency_score)).filter(FeedbackItem.created_at.between(start_dt, end_dt)).scalar() or 0.0

        date_str = target_date.strftime("%Y-%m-%d")
        trend_data.append(TrendPoint(
            date=date_str,
            positive_count=pos_count,
            neutral_count=neu_count,
            negative_count=neg_count,
            avg_urgency=round(float(avg_urgency), 1)
        ))
        
    return trend_data

@router.get("/insights")
async def get_insights(db: Session = Depends(get_db)):
    """Compiles trending topics, volume spikes, and generates PM recommendations."""
    # 1. Local trend detection
    trending_words = trend_detector.detect_trending_keywords(db)
    anomalies = trend_detector.check_anomalies(db)

    # 2. Get latest items for AI summary batching
    recent_items = db.query(FeedbackItem).order_by(FeedbackItem.created_at.desc()).limit(30).all()
    items_list = [{"text": it.text, "category": it.category, "sentiment": it.sentiment_label} for it in recent_items]

    # Generate insights recommendation list (LLM or heuristic)
    ai_recommendations = await ai_engine.generate_insights_from_batch(items_list)

    return {
        "trending_keywords": trending_words,
        "anomalies": anomalies,
        "ai_recommendations": ai_recommendations
    }

@router.post("/model/train")
def train_classifier_model(db: Session = Depends(get_db)):
    """Triggers ML training utilizing manually categorized items from DB."""
    # Fetch all feedback items with non-generic labels
    items = db.query(FeedbackItem).filter(FeedbackItem.category != "General").all()
    
    training_data = [(item.text, item.category) for item in items]

    if not training_data:
        raise HTTPException(
            status_code=400, 
            detail="No categorized feedback items available. Feed or tag feedback first."
        )

    # Instantiate classifier and train
    ml_classifier = MLClassifier()
    success = ml_classifier.train_model(training_data)
    
    if not success:
         raise HTTPException(status_code=500, detail="Model training failed. Make sure you have at least 5 feedback items with diverse categories.")

    # Re-instantiate global categorizer to load newly saved model
    global categorizer
    categorizer = FeedbackCategorizer()
    
    return {"success": True, "message": "ML Classifier retrained successfully."}

@router.get("/integrations", response_model=List[IntegrationConfigResponse])
def get_integrations(db: Session = Depends(get_db)):
    """Retrieves all integration setups."""
    return db.query(IntegrationConfig).all()

@router.put("/integrations/{name}", response_model=IntegrationConfigResponse)
def update_integration(name: str, payload: IntegrationUpdate, db: Session = Depends(get_db)):
    """Updates settings and toggle activation status for specific integration services."""
    config = db.query(IntegrationConfig).filter(IntegrationConfig.name == name).first()
    if not config:
        raise HTTPException(status_code=404, detail="Integration not found")

    config.config_json = payload.config_json
    config.is_active = payload.is_active
    db.commit()
    db.refresh(config)
    return config

@router.post("/simulation/sync-external")
async def simulate_sync_external_reviews(db: Session = Depends(get_db)):
    """Simulates pulling fresh user feedback reviews from iOS App Store, Android Play Store, and G2 Crowd."""
    app_store = AppStoreClient(app_id="123456789")
    play_store = GooglePlayClient(package_name="com.mockapp.mobile")
    g2 = G2Client(product_slug="mock-enterprise-suite")

    fetched_reviews = []
    fetched_reviews.extend(app_store.fetch_latest_reviews())
    fetched_reviews.extend(play_store.fetch_latest_reviews())
    fetched_reviews.extend(g2.fetch_latest_reviews())

    inserted_items = []
    for item in fetched_reviews:
        saved_item = await process_and_save_feedback(
            db,
            text=item["text"],
            source=item["source"],
            rating=item["rating"],
            metadata_json=item["metadata_json"]
        )
        inserted_items.append(saved_item)

    return {
        "success": True,
        "count": len(inserted_items),
        "synced_sources": ["App Store", "Google Play", "G2 Crowd"]
    }

@router.get("/reports/export/csv")
def export_csv(db: Session = Depends(get_db)):
    """Triggers feedback CSV download payload."""
    from fastapi.responses import Response
    csv_data = generate_csv_report(db)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=feedback_report.csv"}
    )

@router.get("/reports/export/html")
def export_html(db: Session = Depends(get_db)):
    """Triggers feedback HTML executive report visual download."""
    from fastapi.responses import HTMLResponse
    html_data = generate_html_report(db)
    return HTMLResponse(content=html_data)
