#!/bin/bash

# Check EventBridge Test Infrastructure Status
# Run this from anywhere in the project

echo "🔍 Checking EventBridge Test Infrastructure..."

# Set region to us-east-1 (required)
export AWS_DEFAULT_REGION=us-east-1
echo "📍 Using region: us-east-1"

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ Error: AWS credentials not configured"
    exit 1
fi

echo "📊 Infrastructure Status:"

# Check DynamoDB table
if aws dynamodb describe-table --table-name cns427-task-api-test-results > /dev/null 2>&1; then
    echo "✅ DynamoDB table: cns427-task-api-test-results"
else
    echo "❌ DynamoDB table: cns427-task-api-test-results (not found)"
fi

# Check Lambda function
if aws lambda get-function --function-name cns427-task-api-test-subscriber > /dev/null 2>&1; then
    echo "✅ Lambda function: cns427-task-api-test-subscriber"
else
    echo "❌ Lambda function: cns427-task-api-test-subscriber (not found)"
fi

# Check EventBridge rule
if aws events list-rules --name-prefix cns427-task-api-test | grep -q "cns427-task-api-test-rule"; then
    echo "✅ EventBridge rule: cns427-task-api-test-rule"
else
    echo "❌ EventBridge rule: cns427-task-api-test-rule (not found)"
fi

echo ""
echo "💡 To deploy infrastructure:"
echo "   make deploy-test-infra"
echo ""
echo "💡 To run EventBridge tests:"
echo "   poetry run pytest tests/integration/test_eventbridge_integration.py -v"