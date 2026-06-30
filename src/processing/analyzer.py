import os
from typing import Dict, Tuple

# Simple local sentiment dictionary for fallback/rule-based analysis
POSITIVE_WORDS = {
    "great", "excellent", "awesome", "love", "perfect", "good", "happy", "satisfied",
    "amazing", "helpful", "wonderful", "easy", "smooth", "fantastic", "best", "useful",
    "correct", "solve", "fixed", "recommend", "superb", "outstanding", "delighted", "efficient"
}

NEGATIVE_WORDS = {
    "bad", "worst", "broken", "slow", "error", "bug", "crash", "fail", "failure",
    "hate", "terrible", "horrible", "difficult", "annoying", "useless", "expensive",
    "poor", "waste", "stuck", "complaint", "issue", "problem", "dissatisfied", "disappointed",
    "frustrated", "unable", "cannot", "leak", "unresponsive"
}

NEGATIONS = {"not", "no", "never", "dont", "cant", "wont", "didnt", "isnt", "wasnt", "havent", "hadnt"}

class SentimentAnalyzer:
    """Performs sentiment analysis using local rule-based lexicography or LLM integration."""

    @classmethod
    def analyze_local(cls, text: str) -> Tuple[float, str]:
        """
        Performs rule-based sentiment calculation.
        Returns a tuple: (sentiment_score [-1.0 to 1.0], sentiment_label)
        """
        if not text:
            return 0.0, "neutral"

        text_lower = text.lower()
        # Clean tokens to search dictionary
        words = [w.strip(".,!?\"'()[]{}") for w in text_lower.split()]
        words = [w for w in words if w]

        score = 0.0
        negate = False

        for i, word in enumerate(words):
            # Check negation
            if word in NEGATIONS:
                negate = True
                continue

            word_val = 0.0
            if word in POSITIVE_WORDS:
                word_val = 1.0
            elif word in NEGATIVE_WORDS:
                word_val = -1.0

            if word_val != 0.0:
                if negate:
                    # Invert the sentiment if preceded by negation within last 2 words
                    word_val = -word_val * 0.5  # slightly attenuated negation
                    negate = False
                score += word_val

        # Normalize score based on words count
        word_count = len(words)
        if word_count == 0:
            return 0.0, "neutral"

        # Squash score between -1.0 and 1.0 using tanh-like scaling
        import math
        normalized = math.tanh(score / 3.0)  # Scaling factor: 3 words of same sentiment reaches ~0.99

        # Determine label
        if normalized >= 0.15:
            label = "positive"
        elif normalized <= -0.15:
            label = "negative"
        else:
            label = "neutral"

        return float(round(normalized, 3)), label

    @classmethod
    async def analyze(cls, text: str, api_key: str = None) -> Tuple[float, str]:
        """
        Main interface for sentiment analysis.
        Uses LLM if key is present; otherwise falls back to local rule-based analyzer.
        """
        # For now, let's fall back to local rule-based analysis.
        # AI/LLM analysis will be orchestrated in the intelligence engine if keys are provided.
        return cls.analyze_local(text)
