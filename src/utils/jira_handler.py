import requests
from datetime import datetime

class JIRAHandler:
    def __init__(self, url, api_token, project_key):
        """Initialize JIRA handler with credentials"""
        self.url = url.rstrip('/')
        self.api_token = api_token
        self.project_key = project_key
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_token}'
        }

    def create_ticket(self, summary, description, severity):
        """Create a JIRA ticket for security finding"""
        endpoint = f"{self.url}/rest/api/2/issue"
        
        # Map severity to priority
        priority_map = {
            'CRITICAL': '1',
            'HIGH': '2',
            'MEDIUM': '3',
            'LOW': '4'
        }
        
        # Format description with markdown
        formatted_description = f"""
h2. Security Finding Details
----
*Severity:* {severity}
*Detection Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

h3. Description
{description}

h3. Recommended Actions
# Investigate the finding details
# Determine if this is a true positive
# Take necessary remediation steps
# Document actions taken
# Close ticket once resolved
        """
        
        payload = {
            'fields': {
                'project': {'key': self.project_key},
                'summary': summary,
                'description': formatted_description,
                'issuetype': {'name': 'Security Issue'},
                'priority': {'id': priority_map.get(severity, '3')},
                'labels': ['security-alert', severity.lower()]
            }
        }
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating JIRA ticket: {str(e)}")
            raise

    def update_ticket(self, ticket_key, comment):
        """Add a comment to existing JIRA ticket"""
        endpoint = f"{self.url}/rest/api/2/issue/{ticket_key}/comment"
        
        payload = {
            'body': comment
        }
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error updating JIRA ticket: {str(e)}")
            raise 