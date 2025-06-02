#!/bin/bash

# Configuration
PROJECT_NAME="security-alerts"
ENVIRONMENT=${1:-prod}  # Default to prod if not specified
REGION=${2:-us-east-1}  # Default to us-east-1 if not specified
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
S3_BUCKET="${PROJECT_NAME}-lambda-${ACCOUNT_ID}"

echo "Deploying to environment: ${ENVIRONMENT}"
echo "AWS Region: ${REGION}"
echo "Account ID: ${ACCOUNT_ID}"

# Create deployment package
echo "Creating deployment package..."
mkdir -p build
pip install -r requirements.txt -t build/
cp -r src/* build/

cd build
zip -r ../security-alerts.zip .
cd ..

# Create S3 bucket if it doesn't exist
echo "Ensuring S3 bucket exists..."
aws s3api create-bucket \
    --bucket ${S3_BUCKET} \
    --region ${REGION} \
    --create-bucket-configuration LocationConstraint=${REGION} || true

# Upload Lambda package to S3
echo "Uploading Lambda package to S3..."
aws s3 cp security-alerts.zip s3://${S3_BUCKET}/

# Deploy CloudFormation stack
echo "Deploying CloudFormation stack..."
aws cloudformation deploy \
    --template-file iac/cloudformation/security-pipeline.yaml \
    --stack-name ${PROJECT_NAME}-${ENVIRONMENT} \
    --parameter-overrides \
        ProjectName=${PROJECT_NAME} \
        Environment=${ENVIRONMENT} \
        JiraInstanceUrl=${JIRA_INSTANCE_URL} \
        JiraProjectKey=${JIRA_PROJECT_KEY} \
        JiraApiToken=${JIRA_API_TOKEN} \
        SlackWebhookUrl=${SLACK_WEBHOOK_URL} \
    --capabilities CAPABILITY_IAM \
    --region ${REGION}

# Clean up
echo "Cleaning up..."
rm -rf build
rm security-alerts.zip

echo "Deployment complete!" 