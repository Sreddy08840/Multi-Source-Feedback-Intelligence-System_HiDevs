import io
import csv
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import FeedbackItem

def generate_csv_report(db: Session) -> str:
    """
    Generates a CSV report of all feedback items in the database.
    """
    items = db.query(FeedbackItem).order_by(FeedbackItem.created_at.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow([
        "ID", "Source", "Rating", "Sentiment Label", "Sentiment Score", 
        "Category", "Urgency Score", "Is Urgent", "Is Trending", 
        "Status", "Assigned To", "Created At", "Text"
    ])
    
    # Rows
    for item in items:
        writer.writerow([
            item.id,
            item.source,
            item.rating if item.rating is not None else "",
            item.sentiment_label or "",
            item.sentiment_score if item.sentiment_score is not None else "",
            item.category or "",
            item.urgency_score or 0.0,
            1 if item.is_urgent else 0,
            1 if item.is_trending else 0,
            item.status,
            item.assigned_to or "",
            item.created_at.isoformat() if item.created_at else "",
            item.text
        ])
        
    return output.getvalue()

def generate_html_report(db: Session) -> str:
    """
    Generates a beautifully styled, stand-alone HTML report of feedback insights.
    """
    items = db.query(FeedbackItem).all()
    total = len(items)
    
    # Compute aggregates
    ratings = [i.rating for i in items if i.rating is not None]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
    
    sentiments = {"positive": 0, "neutral": 0, "negative": 0}
    categories = {}
    urgency_count = 0
    
    for i in items:
        lbl = i.sentiment_label or "neutral"
        sentiments[lbl] = sentiments.get(lbl, 0) + 1
        
        cat = i.category or "General"
        categories[cat] = categories.get(cat, 0) + 1
        
        if i.is_urgent:
            urgency_count += 1

    # Format percentages
    pos_pct = round((sentiments["positive"] / total * 100), 1) if total > 0 else 0
    neu_pct = round((sentiments["neutral"] / total * 100), 1) if total > 0 else 0
    neg_pct = round((sentiments["negative"] / total * 100), 1) if total > 0 else 0
    
    # Recent items HTML table lines
    recent_items = db.query(FeedbackItem).order_by(FeedbackItem.created_at.desc()).limit(10).all()
    rows_html = ""
    for r in recent_items:
        sentiment_badge = f'<span class="badge badge-{r.sentiment_label}">{r.sentiment_label}</span>'
        urgency_badge = f'<span class="badge badge-{"urgent" if r.is_urgent else "normal"}">{r.urgency_score}</span>'
        
        rows_html += f"""
        <tr>
            <td>{r.id}</td>
            <td>{r.source.upper()}</td>
            <td>{r.rating or '-'} ⭐</td>
            <td>{r.category}</td>
            <td>{sentiment_badge}</td>
            <td>{urgency_badge}</td>
            <td class="text-truncate">{r.text[:80]}...</td>
        </tr>
        """

    # HTML template with embedded styling
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Feedback Intelligence System - Executive Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #f8fafc;
            color: #1e293b;
            margin: 0;
            padding: 40px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        }}
        .header {{
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 20px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header h1 {{
            margin: 0;
            color: #0f172a;
            font-size: 24px;
        }}
        .header .date {{
            color: #64748b;
            font-size: 14px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 40px;
        }}
        .card {{
            background: #f1f5f9;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e2e8f0;
        }}
        .card .title {{
            font-size: 14px;
            color: #64748b;
            margin-bottom: 8px;
            text-transform: uppercase;
            font-weight: 600;
        }}
        .card .value {{
            font-size: 28px;
            color: #0f172a;
            font-weight: 700;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            margin-bottom: 20px;
        }}
        th, td {{
            text-align: left;
            padding: 12px 15px;
            border-bottom: 1px solid #e2e8f0;
        }}
        th {{
            background-color: #f8fafc;
            color: #475569;
            font-weight: 600;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 500;
            text-transform: capitalize;
        }}
        .badge-positive {{ background-color: #dcfce7; color: #15803d; }}
        .badge-neutral {{ background-color: #f1f5f9; color: #475569; }}
        .badge-negative {{ background-color: #fee2e2; color: #b91c1c; }}
        .badge-urgent {{ background-color: #fef3c7; color: #d97706; border: 1px solid #f59e0b; }}
        .badge-normal {{ background-color: #f1f5f9; color: #64748b; }}
        .text-truncate {{
            max-width: 400px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .footer {{
            margin-top: 40px;
            text-align: center;
            color: #94a3b8;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>Feedback Intelligence System</h1>
                <p style="margin: 5px 0 0 0; color: #64748b;">Executive Feedback Report</p>
            </div>
            <div class="date">Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</div>
        </div>

        <div class="grid">
            <div class="card">
                <div class="title">Total Ingested</div>
                <div class="value">{total}</div>
            </div>
            <div class="card">
                <div class="title">Avg Rating</div>
                <div class="value">{avg_rating:.2f} ⭐</div>
            </div>
            <div class="card">
                <div class="title">Sentiment Ratio (Pos/Neg)</div>
                <div class="value">{pos_pct}% / {neg_pct}%</div>
            </div>
            <div class="card">
                <div class="title">Urgent Tasks</div>
                <div class="value" style="color: #b91c1c;">{urgency_count}</div>
            </div>
        </div>

        <h2>Latest Customer Feedback</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Source</th>
                    <th>Rating</th>
                    <th>Category</th>
                    <th>Sentiment</th>
                    <th>Urgency</th>
                    <th>Snippet</th>
                </tr>
            </thead>
            <tbody>
                {rows_html if rows_html else '<tr><td colspan="7" style="text-align:center;">No feedback available yet.</td></tr>'}
            </tbody>
        </table>

        <div class="footer">
            Generated automatically by the Feedback Intelligence System Action Layer.
        </div>
    </div>
</body>
</html>
"""
    return html
