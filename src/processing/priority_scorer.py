from typing import Dict, Optional

# Keywords that indicate high urgency
URGENT_KEYWORDS = {
    "urgent", "emergency", "critical", "broken", "crash", "hacked", "leak",
    "security", "fail", "down", "error", "prevent", "blocker", "cannot login",
    "billing issue", "charge twice", "stuck", "immediate", "asap"
}

def calculate_priority(
    text: str,
    sentiment_score: Optional[float],
    category: str,
    rating: Optional[int],
    metadata: Optional[Dict]
) -> tuple[float, bool]:
    """
    Calculates an urgency score between 0.0 and 100.0 based on text features,
    sentiment, ratings, and customer tiers.
    
    Returns:
        (urgency_score: float, is_urgent: bool)
    """
    score = 0.0

    # 1. Sentiment Score Factor (Up to 40 points)
    # sentiment_score is between -1.0 and 1.0. Negative sentiment increases urgency.
    if sentiment_score is not None:
        if sentiment_score < 0:
            # -1.0 sentiment yields 40 points, 0 sentiment yields 0 points
            score += abs(sentiment_score) * 40.0
        elif sentiment_score > 0.5:
            # High positive sentiment reduces urgency score
            score -= (sentiment_score - 0.5) * 10.0

    # 2. Rating Factor (Up to 30 points)
    if rating is not None:
        if rating == 1:
            score += 30.0
        elif rating == 2:
            score += 15.0
        elif rating == 3:
            score += 5.0

    # 3. Urgent Keyword Factor (Up to 20 points)
    if text:
        text_lower = text.lower()
        matches = sum(1 for kw in URGENT_KEYWORDS if kw in text_lower)
        if matches > 0:
            score += min(20.0, matches * 10.0)

    # 4. Category Factor (Up to 15 points)
    category_weights = {
        "Bug": 15.0,
        "Pricing/Billing": 10.0,
        "Support": 10.0,
        "UI/UX": 5.0,
        "Feature Request": 0.0,
        "General": 0.0
    }
    score += category_weights.get(category, 0.0)

    # 5. Metadata segment weight (e.g. VIP/Enterprise) (Up to 15 points)
    if metadata and isinstance(metadata, dict):
        segment = metadata.get("segment", "").lower()
        if segment in ("vip", "enterprise", "premium"):
            score += 15.0

    # Bind score between 0.0 and 100.0
    score = max(0.0, min(100.0, score))
    score = round(score, 1)

    # Flag as urgent if score is 60 or above
    is_urgent = score >= 60.0

    return score, is_urgent
