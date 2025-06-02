# AWS Security Alerting Project

## Overview
This project implements a **full AWS Security Alerting pipeline** by integrating **GuardDuty** and **Security Hub** findings with automated notifications to **JIRA** and **Slack** using **AWS Lambda** and **SNS**. The solution provides real-time visibility into security issues and accelerates incident response by connecting AWS-native tools with external ticketing and communication systems.

---

## Architecture Diagram
```
GuardDuty → Security Hub → SNS Topic → Lambda → JIRA / Slack
```

---

## Tools Used
✅ AWS GuardDuty  
✅ AWS Security Hub  
✅ AWS Lambda (Python)  
✅ AWS SNS (Simple Notification Service)  
✅ JIRA REST API  
✅ Slack Webhook API  
✅ IAM Roles & Policies  
✅ CloudWatch Logs

---

## Step-by-Step Walkthrough

### **Step 1: Enable GuardDuty and Security Hub**
1. Go to the AWS console → **GuardDuty** → Enable.
2. Go to the AWS console → **Security Hub** → Enable → Integrate GuardDuty as a data source.

### **Step 2: Create SNS Topic**
1. Navigate to **SNS** → Create Topic → Name it `SecurityAlerts`.
2. Create a new **Subscription** (e.g., email) to test delivery.
3. Note the SNS Topic ARN.

### **Step 3: Create IAM Role for Lambda**
1. Go to **IAM** → Roles → Create Role.
2. Select **Lambda** as trusted entity.
3. Attach permissions:
    - `AWSLambdaBasicExecutionRole`
    - `AmazonSNSFullAccess`
    - Custom policy to allow `securityhub:GetFindings` and `guardduty:GetFindings`.
4. Save the Role ARN.

### **Step 4: Create Lambda Function**
1. Go to **Lambda** → Create Function → Author from scratch.
2. Runtime: Python 3.x
3. Attach the IAM Role created above.
4. Add an SNS Trigger linked to the `SecurityAlerts` topic.

### **Step 5: Write Lambda Code**
- The Lambda function will:
    - Parse incoming SNS message.
    - Extract relevant details from GuardDuty or Security Hub findings.
    - Format and send a POST request to JIRA (using REST API) and Slack (using Incoming Webhook).

Example (simplified Python snippet):
```python
import json, requests

def lambda_handler(event, context):
    message = json.loads(event['Records'][0]['Sns']['Message'])
    alert_summary = message['detail']['title']
    
    # Send to Slack
    slack_webhook_url = 'https://hooks.slack.com/services/XXXXX'
    slack_data = {'text': f'New Security Alert: {alert_summary}'}
    requests.post(slack_webhook_url, json=slack_data)

    # Create JIRA ticket
    jira_url = 'https://your-domain.atlassian.net/rest/api/2/issue'
    jira_headers = {'Content-Type': 'application/json'}
    jira_data = {
        "fields": {
            "project": {"key": "SEC"},
            "summary": alert_summary,
            "description": json.dumps(message),
            "issuetype": {"name": "Task"}
        }
    }
    requests.post(jira_url, headers=jira_headers, auth=('email', 'api_token'), json=jira_data)
```

### **Step 6: Test End-to-End**
1. Trigger a GuardDuty finding manually or wait for a real detection.
2. Ensure the alert flows:
    - GuardDuty → Security Hub → SNS → Lambda → JIRA & Slack.
3. Check CloudWatch Logs for debugging.

### **Step 7: Secure & Harden**
- Use AWS Secrets Manager to store JIRA and Slack credentials.
- Add error handling and retries in Lambda code.
- Set up CloudWatch Alarms for Lambda failures.

### **Step 8: Extend**
- Integrate with PagerDuty or ServiceNow.
- Add prioritization logic based on severity.
- Aggregate similar findings to avoid alert fatigue.

---

## Repo Structure
```
aws-security-alerting-project/
├── lambda_function.py        # Main Lambda handler code
├── README.md                 # Project description and walkthrough
├── requirements.txt          # Python dependencies
└── sample_event.json         # Example SNS event payload
```

---

## Final Notes
✅ This project accelerates cloud security response by combining AWS-native security services with external collaboration tools.  
✅ It’s designed to be modular and extendable for future integrations.
