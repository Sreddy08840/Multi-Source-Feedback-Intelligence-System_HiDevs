import re

def clean_text(text: str) -> str:
    """
    Cleans raw feedback text by:
    - Removing HTML tags.
    - Normalizing whitespace (newlines, tabs, multiple spaces).
    - Trimming leading/trailing spaces.
    """
    if not text:
        return ""

    # Remove HTML tags using regex
    cleaned = re.sub(r"<[^>]+>", " ", text)

    # Replace newlines, tabs, and multiple spaces with a single space
    cleaned = re.sub(r"\s+", " ", cleaned)

    # Trim leading/trailing spaces
    cleaned = cleaned.strip()

    return cleaned
