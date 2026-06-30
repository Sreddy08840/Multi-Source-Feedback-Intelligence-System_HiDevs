import logging
from sqlalchemy.orm import Session
from ..models import IntegrationConfig, FeedbackItem

logger = logging.getLogger(__name__)

def trigger_urgency_alert(db: Session, item: FeedbackItem) -> bool:
    """
    Sends alerts (e.g., Slack or Microsoft Teams webhook posts) when a critical
    or urgent feedback item is ingested.
    """
    if not item.is_urgent:
        return False

    # Check database config for Slack integration
    slack_config = db.query(IntegrationConfig).filter(
        IntegrationConfig.name == "slack",
        IntegrationConfig.is_active == True
    ).first()

    # Check for Teams integration
    teams_config = db.query(IntegrationConfig).filter(
        IntegrationConfig.name == "teams",
        IntegrationConfig.is_active == True
    ).first()

    triggered = False

    # Simulate sending the Slack Alert
    if slack_config:
        webhook_url = slack_config.config_json.get("webhook_url", "https://hooks.slack.com/services/mock")
        alert_payload = {
            "text": f"🚨 *URGENT CUSTOMER FEEDBACK DETECTED* 🚨\n"
                    f"*Source:* {item.source.capitalize()}\n"
                    f"*Category:* {item.category}\n"
                    f"*Urgency Score:* {item.urgency_score}/100\n"
                    f"*Rating:* {item.rating or 'N/A'} ⭐\n"
                    f"*Feedback:* \"{item.text}\"\n"
                    f"*Action Required:* Please review in the Feedback Dashboard."
        }
        logger.info(f"[SLACK ALERT TRIGGERED] Post to {webhook_url}: {alert_payload['text']}")
        triggered = True

    # Simulate sending the Teams Alert
    if teams_config:
        webhook_url = teams_config.config_json.get("webhook_url", "https://outlook.office.com/webhook/mock")
        alert_payload = {
            "title": "🚨 URGENT CUSTOMER FEEDBACK DETECTED",
            "text": f"**Source:** {item.source.capitalize()}<br/>"
                    f"**Category:** {item.category}<br/>"
                    f"**Urgency Score:** {item.urgency_score}/100<br/>"
                    f"**Rating:** {item.rating or 'N/A'} Stars<br/>"
                    f"**Content:** \"{item.text}\""
        }
        logger.info(f"[TEAMS ALERT TRIGGERED] Post to {webhook_url}: {alert_payload['title']}")
        triggered = True

    # Default console warning if no integrations are configured
    if not triggered:
        logger.warning(
            f"Urgent feedback #{item.id} received (Score: {item.urgency_score}). "
            f"No active notification integrations configured."
        )

    return triggered
