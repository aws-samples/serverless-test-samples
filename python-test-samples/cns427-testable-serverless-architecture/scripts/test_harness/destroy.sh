#!/bin/bash

# Destroy EventBridge Test Infrastructure
# Run this from anywhere in the project (via make destroy-test-infra)

set -e

echo "🗑️  Destroying EventBridge Test Infrastructure..."

# Get script directory and change to infrastructure/test_harness
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"
cd "$PROJECT_ROOT/infrastructure/test_harness"

# Set region to us-east-1 (required)
export AWS_DEFAULT_REGION=us-east-1
echo "📍 Using region: us-east-1"

# Check if CDK is installed
if ! command -v cdk &> /dev/null; then
    echo "❌ Error: CDK is not installed"
    exit 1
fi

echo "🔍 Synthesizing CDK stack..."
if ! cdk synth > /dev/null 2>&1; then
    echo "⚠️  CDK synthesis failed, but continuing with destroy..."
fi

echo "☁️  Destroying AWS resources..."
if cdk destroy --force; then
    echo "✅ Test infrastructure destroyed successfully!"
    
    # Clean up CDK output
    rm -rf cdk.out
    
else
    echo "❌ Destruction failed"
    exit 1
fi