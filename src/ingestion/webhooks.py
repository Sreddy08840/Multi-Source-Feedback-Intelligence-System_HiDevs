from typing import Dict, Any, Optional

def parse_webhook_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standardizes contact form payloads into the unified feedback ingestion format.
    Handles fields like name, email, feedback/message, and rating.
    """
    # Look for common field names representing the feedback text
    text_fields = ["message", "text", "feedback", "comments", "body"]
    text = ""
    for field in text_fields:
        if field in payload and payload[field]:
            text = str(payload[field])
            break

    # Look for ratings
    rating_fields = ["rating", "stars", "score"]
    rating: Optional[int] = None
    for field in rating_fields:
        if field in payload and payload[field] is not None:
            try:
                val = int(payload[field])
                if 1 <= val <= 5:
                    rating = val
                    break
            except (ValueError, TypeError):
                continue

    # Extract user metadata
    email = payload.get("email") or payload.get("email_address")
    name = payload.get("name") or payload.get("fullname")
    user_id = payload.get("user_id")

    metadata = {}
    if email:
        metadata["email"] = email
    if name:
        metadata["name"] = name
    if user_id:
        metadata["user_id"] = user_id
    if "ip" in payload:
        metadata["ip"] = payload["ip"]

    return {
        "text": text,
        "rating": rating,
        "source": "web",
        "metadata_json": metadata
    }
