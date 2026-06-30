import re
from typing import Dict, Any

def parse_raw_email(raw_email: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses a raw email dictionary (e.g. from an IMAP listener) containing:
      - 'from': Sender email
      - 'subject': Email subject line
      - 'body': Email plain text body
    
    Returns standard ingestion format.
    """
    sender = raw_email.get("from", "unknown@example.com")
    subject = raw_email.get("subject", "").strip()
    body = raw_email.get("body", "").strip()

    # Clean subject
    subject_cleaned = re.sub(r"^(re|fwd|fw):\s*", "", subject, flags=re.IGNORECASE).strip()

    # Combine subject and body for analysis
    full_text = f"Subject: {subject_cleaned}\n\n{body}" if subject_cleaned else body

    # Extract any potential signature / footer elements to keep cleaner
    # (simplistic trim of standard email footers)
    body_cleaned = body.split("\n--\n")[0].split("\nRegards,")[0].split("\nSent from my")[0]
    
    # We can also attempt to look for ratings inside the email if it was a survey response
    # e.g., "Rating: 4/5" or "Score: 5"
    rating = None
    rating_match = re.search(r"\b(?:rating|score|stars):\s*([1-5])\b", body.lower())
    if rating_match:
        rating = int(rating_match.group(1))

    return {
        "text": full_text,
        "rating": rating,
        "source": "email",
        "metadata_json": {
            "sender": sender,
            "subject": subject,
            "body_snippet": body_cleaned[:150]
        }
    }
