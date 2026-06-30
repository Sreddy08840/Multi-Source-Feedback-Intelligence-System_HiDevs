import io
import csv
from typing import Dict, List, Any

# Column header options to scan for
TEXT_HEADERS = {"text", "feedback", "comment", "comments", "message", "body", "description"}
RATING_HEADERS = {"rating", "stars", "score", "rating_score"}
SOURCE_HEADERS = {"source", "channel", "platform"}

def parse_csv_file(file_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Parses CSV file contents from bytes, auto-detects columns for text,
    rating, and source, and returns unified feedback schemas.
    """
    # Decode bytes to string
    try:
        content = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        content = file_bytes.decode("latin-1")

    # Read CSV
    f = io.StringIO(content)
    reader = csv.reader(f)

    # Read headers
    try:
        headers = next(reader)
    except StopIteration:
        return []

    # Map headers to standard fields
    headers_lower = [h.strip().lower() for h in headers]
    
    text_idx = -1
    rating_idx = -1
    source_idx = -1

    for idx, h in enumerate(headers_lower):
        if h in TEXT_HEADERS and text_idx == -1:
            text_idx = idx
        elif h in RATING_HEADERS and rating_idx == -1:
            rating_idx = idx
        elif h in SOURCE_HEADERS and source_idx == -1:
            source_idx = idx

    # Fallback to column indices if no header match
    if text_idx == -1 and len(headers) > 0:
        # Assume first column is text
        text_idx = 0
    if rating_idx == -1 and len(headers) > 1:
        # Assume second column is rating if it exists
        # We will validate numbers later
        rating_idx = 1

    parsed_items = []
    
    for row in reader:
        if not row:
            continue
        
        # Extract text
        text = ""
        if 0 <= text_idx < len(row):
            text = row[text_idx].strip()
        
        if not text:
            continue  # Skip rows without feedback text

        # Extract rating
        rating = None
        if 0 <= rating_idx < len(row):
            try:
                val = int(row[rating_idx].strip())
                if 1 <= val <= 5:
                    rating = val
            except (ValueError, TypeError):
                pass

        # Extract source
        source = "file"
        if 0 <= source_idx < len(row):
            src_val = row[source_idx].strip().lower()
            if src_val:
                source = f"file_{src_val}"

        # Standard item dict
        parsed_items.append({
            "text": text,
            "rating": rating,
            "source": source,
            "metadata_json": {
                "import_method": "csv_upload",
                "original_row_length": len(row)
            }
        })

    return parsed_items
