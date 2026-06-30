import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta

from src.database import engine, SessionLocal, Base
from src.models import IntegrationConfig, FeedbackItem
from src.api.endpoints import router as api_router
from src.api.middleware import RequestLoggingMiddleware

# Configure logging formats
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize database schema tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Feedback Intelligence System API",
    description="REST API to ingest, clean, categorize, evaluate sentiment, and route multi-source customer feedback.",
    version="1.0.0"
)

# CORS Policy configuration (allowing local react frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local development simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom log trackers
app.add_middleware(RequestLoggingMiddleware)

# Register route coordinates
app.include_router(api_router, prefix="/api")

# Auto-seed database during initialization if empty
@app.on_event("startup")
def startup_db_seed():
    db = SessionLocal()
    try:
        # Seed integrations if table is empty
        if db.query(IntegrationConfig).count() == 0:
            logger.info("Database empty. Seeding default integration configs...")
            default_integrations = [
                IntegrationConfig(
                    name="slack",
                    config_json={"webhook_url": "https://hooks.slack.com/services/T00/B00/mock"},
                    is_active=True
                ),
                IntegrationConfig(
                    name="teams",
                    config_json={"webhook_url": "https://outlook.office.com/webhook/mock"},
                    is_active=False
                ),
                IntegrationConfig(
                    name="jira",
                    config_json={"project_key": "FEED", "api_token": "mock-token"},
                    is_active=True
                ),
                IntegrationConfig(
                    name="salesforce",
                    config_json={"instance_url": "https://mock-salesforce.com"},
                    is_active=False
                )
            ]
            db.add_all(default_integrations)
            db.commit()

        # Seed sample feedback historical items to populate charts out-of-the-box
        if db.query(FeedbackItem).count() == 0:
            logger.info("Database empty. Seeding sample historical feedback data...")
            now = datetime.utcnow()
            
            # Helper to quickly generate pre-processed seed items
            from src.processing.cleaner import clean_text
            from src.processing.analyzer import SentimentAnalyzer
            from src.processing.categorizer import FeedbackCategorizer
            from src.processing.priority_scorer import calculate_priority

            seed_texts = [
                ("The checkout payment crashed twice when using Apple Pay on mobile. Unusable!", "web", 1, now - timedelta(days=5), {"email": "john.doe@example.com"}),
                ("Great app, our productivity rose significantly! Very easy layout.", "api_appstore", 5, now - timedelta(days=4), {"reviewer": "pro_user"}),
                ("My invoice was incorrect; I was charged for the premium plan twice. Urgent fix needed.", "email", 1, now - timedelta(days=3), {"sender": "finance@corporate.com", "segment": "VIP"}),
                ("Could you please implement a dark mode screen? Bright styling causes eye strain.", "api_googleplay", 4, now - timedelta(days=3), {"reviewer": "night_owl"}),
                ("Decent dashboard, but the navigation menus are confusing to locate.", "api_g2", 3, now - timedelta(days=2), {"segment": "Enterprise"}),
                ("The loading speeds are extremely slow when loading large datasets. It hangs.", "web", 2, now - timedelta(days=2), {"email": "dev_analyst@company.com"}),
                ("Outstanding customer service response times. Highly recommend this team.", "email", 5, now - timedelta(days=1), {"sender": "client_support@vendor.com"}),
                ("The app works well, but it is missing integration features with Slack.", "api_appstore", 3, now, {"reviewer": "team_lead"}),
                ("Error code 500 when exporting data to CSV. Core functionality is broken.", "web", 1, now, {"email": "lead_eng@techcorp.com"})
            ]

            categorizer_local = FeedbackCategorizer()

            for text, source, rating, created_at, metadata in seed_texts:
                cleaned = clean_text(text)
                sent_score, sent_lbl = SentimentAnalyzer.analyze_local(cleaned)
                category = categorizer_local.categorize(cleaned)
                urg_score, is_urg = calculate_priority(cleaned, sent_score, category, rating, metadata)

                item = FeedbackItem(
                    text=text,
                    cleaned_text=cleaned,
                    source=source,
                    rating=rating,
                    sentiment_score=sent_score,
                    sentiment_label=sent_lbl,
                    category=category,
                    urgency_score=urg_score,
                    is_urgent=is_urg,
                    status="new",
                    metadata_json=metadata,
                    created_at=created_at
                )
                db.add(item)
            
            db.commit()
            logger.info("Feedback database seeding completed successfully.")

    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Feedback Intelligence System",
        "documentation_url": "/docs"
    }
