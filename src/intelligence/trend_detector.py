import re
from datetime import datetime, timedelta
from typing import Dict, List, Any
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..models import FeedbackItem

COMMON_STOPWORDS = {
    "the", "a", "and", "is", "of", "to", "in", "it", "i", "you", "that", "this",
    "was", "for", "on", "with", "as", "at", "by", "an", "be", "have", "are", "from",
    "my", "we", "weve", "they", "them", "their", "there", "our", "your", "me", "am"
}

class TrendDetector:
    """Analyzes feedback to extract trending terms, identify volume spikes, and detect anomalies."""

    @staticmethod
    def extract_terms(text: str) -> List[str]:
        """Splits text into alphanumeric tokens, filtering out stop words and short terms."""
        if not text:
            return []
        tokens = re.findall(r"\b\w{3,15}\b", text.lower())
        return [t for t in tokens if t not in COMMON_STOPWORDS]

    def detect_trending_keywords(self, db: Session, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Detects keywords that have spiked in frequency in the last 7 days compared to older data.
        Returns a list of dicts: [{'word': str, 'recent_count': int, 'score': float}]
        """
        # Fetch items from last 7 days vs previous period
        now = datetime.utcnow()
        seven_days_ago = now - timedelta(days=7)
        fourteen_days_ago = now - timedelta(days=14)

        recent_items = db.query(FeedbackItem).filter(FeedbackItem.created_at >= seven_days_ago).all()
        older_items = db.query(FeedbackItem).filter(
            FeedbackItem.created_at >= fourteen_days_ago,
            FeedbackItem.created_at < seven_days_ago
        ).all()

        recent_counts = {}
        for item in recent_items:
            for word in self.extract_terms(item.cleaned_text or item.text):
                recent_counts[word] = recent_counts.get(word, 0) + 1

        older_counts = {}
        for item in older_items:
            for word in self.extract_terms(item.cleaned_text or item.text):
                older_counts[word] = older_counts.get(word, 0) + 1

        trends = []
        for word, r_count in recent_counts.items():
            o_count = older_counts.get(word, 0)
            # If a word is frequently appearing recently, calculate spike score
            # Score = (Recent Count - Older Count) / (Older Count + 1)
            score = (r_count - o_count) / (o_count + 1.0)
            if r_count >= 2:  # Must occur at least twice recently to be a trend
                trends.append({
                    "word": word,
                    "recent_count": r_count,
                    "historical_count": o_count,
                    "score": round(score, 2)
                })

        # Sort by spike score, then by volume
        trends.sort(key=lambda x: (x["score"], x["recent_count"]), reverse=True)
        return trends[:limit]

    def check_anomalies(self, db: Session) -> Dict[str, Any]:
        """
        Checks for unusual volume spikes or negative sentiment spikes in the last 24 hours.
        """
        now = datetime.utcnow()
        one_day_ago = now - timedelta(days=1)
        eight_days_ago = now - timedelta(days=8)

        # 1. Volume Spikes
        recent_count = db.query(FeedbackItem).filter(FeedbackItem.created_at >= one_day_ago).count()
        
        # Calculate daily average over previous 7 days
        daily_volumes = []
        for i in range(1, 8):
            start = now - timedelta(days=i+1)
            end = now - timedelta(days=i)
            cnt = db.query(FeedbackItem).filter(FeedbackItem.created_at >= start, FeedbackItem.created_at < end).count()
            daily_volumes.append(cnt)

        avg_daily_volume = sum(daily_volumes) / len(daily_volumes) if daily_volumes else 0.0

        # Anomaly if volume in last 24h is more than 3x the average (and at least 5 feedback items)
        volume_anomaly = recent_count >= 5 and (recent_count > avg_daily_volume * 3.0 or avg_daily_volume == 0)

        # 2. Negative Sentiment Spike
        recent_negatives = db.query(FeedbackItem).filter(
            FeedbackItem.created_at >= one_day_ago,
            FeedbackItem.sentiment_label == "negative"
        ).count()

        recent_positives = db.query(FeedbackItem).filter(
            FeedbackItem.created_at >= one_day_ago,
            FeedbackItem.sentiment_label == "positive"
        ).count()

        neg_ratio = recent_negatives / (recent_negatives + recent_positives) if (recent_negatives + recent_positives) > 0 else 0.0
        sentiment_anomaly = recent_negatives >= 3 and neg_ratio >= 0.60

        return {
            "volume_anomaly_detected": volume_anomaly,
            "recent_volume": recent_count,
            "avg_historical_volume": round(avg_daily_volume, 1),
            "sentiment_anomaly_detected": sentiment_anomaly,
            "negative_feedback_ratio": round(neg_ratio * 100, 1),
            "anomaly_flag": volume_anomaly or sentiment_anomaly
        }
