import os
import re
from typing import Dict, List, Optional
from ..intelligence.ml_models import MLClassifier

# Keyword dictionaries for rule-based cold-start classification
CATEGORY_KEYWORDS = {
    "Bug": [
        "bug", "crash", "error", "exception", "freeze", "broken", "fail", "glitch",
        "faulty", "not working", "loop", "hangs", "stops", "breaks", "wrong", "malfunction"
    ],
    "Feature Request": [
        "add", "feature", "request", "suggest", "wish", "want", "hope", "improve",
        "option", "would like", "should have", "can we", "ideas", "allow", "support for"
    ],
    "Pricing/Billing": [
        "price", "cost", "expensive", "charge", "fee", "billing", "subscribe", "payment",
        "cheap", "invoice", "refund", "subscription", "plan", "transactions", "card", "pay"
    ],
    "UI/UX": [
        "design", "color", "button", "font", "layout", "screen", "display", "interface",
        "dark mode", "menu", "look", "feel", "clunky", "confusing", "intuitive", "navigation"
    ],
    "Support": [
        "support", "help", "ticket", "contact", "response", "representative", "agent",
        "chat", "reply", "answer", "slow service", "no response", "assistance"
    ]
}

class FeedbackCategorizer:
    """Categorizes feedback using rules or machine learning."""

    def __init__(self):
        # We will check if the ML classifier is trained.
        self.ml_classifier = MLClassifier()

    def categorize_rules(self, text: str) -> str:
        """
        Uses keyword matching to score each category.
        Returns the category with the highest matching score, or 'General' as fallback.
        """
        if not text:
            return "General"

        text_lower = text.lower()
        scores = {cat: 0 for cat in CATEGORY_KEYWORDS}

        for cat, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                # Use regex word boundaries or substring search
                if kw in text_lower:
                    scores[cat] += 1
                # Give extra weight to explicit matches on keywords at the beginning
                if text_lower.startswith(kw):
                    scores[cat] += 2

        max_score = 0
        best_cat = "General"
        for cat, score in scores.items():
            if score > max_score:
                max_score = score
                best_cat = cat

        return best_cat

    def categorize(self, text: str) -> str:
        """
        Categorize feedback text.
        Falls back to rule-based keyword matching if ML model is not trained.
        """
        # Try to predict using ML
        ml_prediction = self.ml_classifier.predict(text)
        if ml_prediction:
            return ml_prediction

        # Rule-based fallback
        return self.categorize_rules(text)
