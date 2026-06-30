import pytest
from src.processing.cleaner import clean_text
from src.processing.analyzer import SentimentAnalyzer
from src.processing.categorizer import FeedbackCategorizer
from src.processing.priority_scorer import calculate_priority

def test_clean_text():
    # Test HTML removal
    assert clean_text("<p>Hello <b>World</b></p>") == "Hello World"
    # Test whitespace compression
    assert clean_text("  This  \n   is   \t a text.  ") == "This is a text."
    # Test empty string
    assert clean_text("") == ""

def test_sentiment_analyzer():
    # Test local positive sentiment
    score, label = SentimentAnalyzer.analyze_local("This is a great and wonderful app! Highly recommend.")
    assert label == "positive"
    assert score > 0.0

    # Test local negative sentiment
    score, label = SentimentAnalyzer.analyze_local("Very slow loading times and terrible crash bug.")
    assert label == "negative"
    assert score < 0.0

    # Test negation handling
    score_not_good, label_not_good = SentimentAnalyzer.analyze_local("This product is not good.")
    assert score_not_good < 0.15  # Negation pulls sentiment down

def test_categorizer():
    cat = FeedbackCategorizer()
    
    # Test bug keyword
    assert cat.categorize_rules("The application crashed after update") == "Bug"
    # Test billing keyword
    assert cat.categorize_rules("Why did you charge me twice on my credit card?") == "Pricing/Billing"
    # Test UI keyword
    assert cat.categorize_rules("I really like the dark mode and color scheme design") == "UI/UX"
    # Test fallback
    assert cat.categorize_rules("random text without triggers") == "General"

def test_priority_scorer():
    # Test high priority: VIP + Neg sentiment + Low rating + Urgent keyword
    score, is_urgent = calculate_priority(
        text="Critical crash issue. App is completely down!",
        sentiment_score=-0.8,
        category="Bug",
        rating=1,
        metadata={"segment": "VIP"}
    )
    assert is_urgent is True
    assert score >= 75.0

    # Test low priority: positive feedback, high rating, general
    score_low, is_urgent_low = calculate_priority(
        text="I love this, it's amazing and working nicely.",
        sentiment_score=0.9,
        category="General",
        rating=5,
        metadata=None
    )
    assert is_urgent_low is False
    assert score_low <= 15.0
