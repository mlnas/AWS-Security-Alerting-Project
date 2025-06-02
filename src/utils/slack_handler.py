import json
import requests

class SlackHandler:
    def __init__(self, webhook_url):
        """Initialize Slack handler with webhook URL"""
        self.webhook_url = webhook_url

    def send_notification(self, title, severity, description, jira_ticket):
        """Send formatted Slack notification"""
        
        # Color coding based on severity
        color_map = {
            'CRITICAL': '#FF0000',  # Red
            'HIGH': '#FFA500',      # Orange
            'MEDIUM': '#FFFF00',    # Yellow
            'LOW': '#00FF00'        # Green
        }
        
        # Create Slack message blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🚨 New Security Alert",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Title:*\n{title}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Severity:*\n{severity}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Description:*\n{description[:500]}..."
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*JIRA Ticket:* <{jira_ticket}|{jira_ticket}>"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "🔍 Please investigate and update the JIRA ticket with findings"
                    }
                ]
            }
        ]
        
        # Prepare payload
        payload = {
            "blocks": blocks,
            "attachments": [
                {
                    "color": color_map.get(severity, '#808080'),
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "React to this message to acknowledge:"
                            }
                        }
                    ]
                }
            ]
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload
            )
            response.raise_for_status()
            return {"status": "sent"}
        except requests.exceptions.RequestException as e:
            print(f"Error sending Slack notification: {str(e)}")
            raise 