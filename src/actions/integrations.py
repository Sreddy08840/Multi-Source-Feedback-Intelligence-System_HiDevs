import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models import IntegrationConfig, FeedbackItem

logger = logging.getLogger(__name__)

def create_jira_ticket(db: Session, item: FeedbackItem) -> Dict[str, Any]:
    """
    Creates a Jira ticket for bug reports or critical complaints.
    Can be run automatically or manually from the dashboard.
    """
    jira_config = db.query(IntegrationConfig).filter(
        IntegrationConfig.name == "jira"
    ).first()

    is_active = jira_config.is_active if jira_config else False
    project_key = jira_config.config_json.get("project_key", "FEED") if (jira_config and jira_config.config_json) else "FEED"

    # Generate mock ticket key
    ticket_num = 1000 + item.id
    ticket_key = f"{project_key}-{ticket_num}"
    ticket_url = f"https://jira.mock-workspace.atlassian.net/browse/{ticket_key}"

    log_msg = (
        f"[JIRA INTEGRATION] Created ticket {ticket_key} for Feedback #{item.id} "
        f"(Category: {item.category}, Urgent: {item.is_urgent}). Link: {ticket_url}"
    )
    logger.info(log_msg)

    return {
        "success": True,
        "integration_active": is_active,
        "ticket_key": ticket_key,
        "ticket_url": ticket_url,
        "summary": f"[{item.category}] Feedback Ref #{item.id} ({item.source})",
        "description": item.text
    }

def sync_to_salesforce(db: Session, item: FeedbackItem) -> Dict[str, Any]:
    """
    Syncs user details and feedback content to a Salesforce CRM Contact/Lead page.
    """
    sf_config = db.query(IntegrationConfig).filter(
        IntegrationConfig.name == "salesforce"
    ).first()

    is_active = sf_config.is_active if sf_config else False
    
    # Generate mock Lead ID
    lead_id = f"00Q8000000{item.id:06d}X"
    lead_url = f"https://salesforce.mock-instance.com/lightning/r/Lead/{lead_id}/view"

    log_msg = (
        f"[SALESFORCE CRM] Synchronized Feedback #{item.id} to Lead ID {lead_id}. "
        f"URL: {lead_url}"
    )
    logger.info(log_msg)

    return {
        "success": True,
        "integration_active": is_active,
        "lead_id": lead_id,
        "lead_url": lead_url,
        "sync_time": item.created_at.isoformat() if item.created_at else None
    }
