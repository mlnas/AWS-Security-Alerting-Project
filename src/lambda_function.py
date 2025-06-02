import json
import os
import boto3
from utils.jira_handler import JIRAHandler
from utils.slack_handler import SlackHandler
from utils.finding_parser import FindingParser

# Initialize AWS clients
secrets = boto3.client('secretsmanager')
securityhub = boto3.client('securityhub')
guardduty = boto3.client('guardduty')

def get_secret(secret_name):
    """Retrieve secret from AWS Secrets Manager"""
    try:
        response = secrets.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except Exception as e:
        print(f"Error retrieving secret {secret_name}: {str(e)}")
        raise

def lambda_handler(event, context):
    """Main Lambda handler function"""
    try:
        # Parse SNS message
        sns_message = json.loads(event['Records'][0]['Sns']['Message'])
        
        # Initialize parser and handlers
        parser = FindingParser(sns_message)
        finding_details = parser.parse()
        
        # Get secrets
        jira_secrets = get_secret('security-alerts/jira')
        slack_secrets = get_secret('security-alerts/slack')
        
        # Initialize handlers
        jira = JIRAHandler(
            url=jira_secrets['instance_url'],
            api_token=jira_secrets['api_token'],
            project_key=jira_secrets['project_key']
        )
        
        slack = SlackHandler(
            webhook_url=slack_secrets['webhook_url']
        )
        
        # Create JIRA ticket
        jira_response = jira.create_ticket(
            summary=finding_details['title'],
            description=finding_details['description'],
            severity=finding_details['severity']
        )
        
        # Send Slack notification
        slack_response = slack.send_notification(
            title=finding_details['title'],
            severity=finding_details['severity'],
            description=finding_details['description'],
            jira_ticket=jira_response['key']
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Successfully processed security finding',
                'jiraTicket': jira_response['key'],
                'slackNotification': 'sent'
            })
        }
        
    except Exception as e:
        print(f"Error processing security finding: {str(e)}")
        raise 