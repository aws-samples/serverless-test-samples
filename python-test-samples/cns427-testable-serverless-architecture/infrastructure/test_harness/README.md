# EventBridge Test Infrastructure

Simple setup for EventBridge integration testing infrastructure in **us-east-1** region.

## Quick Start

1. **Set AWS credentials** (use the export commands provided):
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_SESSION_TOKEN=your_session_token
   ```

2. **Deploy infrastructure** (from project root):
   ```bash
   make deploy-test-infra
   ```

3. **Run EventBridge tests**:
   ```bash
   poetry run pytest tests/integration/test_eventbridge_integration.py -v
   ```

## Commands (from project root)

- **Deploy**: `make deploy-test-infra` - Deploy test infrastructure
- **Check**: `make check-test-infra` - Check infrastructure status  
- **Destroy**: `make destroy-test-infra` - Clean up infrastructure

Or run directly from this directory:
- **Deploy**: `poetry run ./deploy.sh`
- **Check**: `poetry run ./check.sh`  
- **Destroy**: `poetry run ./destroy.sh`

## What Gets Deployed (us-east-1 region)

- **DynamoDB Table**: `cns427-task-api-test-results` - Stores captured test events
- **Lambda Function**: `cns427-task-api-test-subscriber` - Captures EventBridge events
- **EventBridge Rule**: `cns427-task-api-test-rule` - Routes TEST-* events to Lambda

**Note**: All resources are deployed in us-east-1 region as required.

## Files

- `test_infrastructure_stack.py` - CDK stack definition
- `test_subscriber.py` - Lambda function code
- `deploy.sh` - Deployment script
- `destroy.sh` - Cleanup script  
- `check.sh` - Status check script

## Troubleshooting

1. **CDK not found**: Install with `npm install -g aws-cdk`
2. **Python dependencies**: Run `pip install aws-cdk-lib constructs boto3`
3. **AWS credentials**: Set the export commands provided
4. **Synthesis fails**: Check `test_infrastructure_stack.py` for errors

The scripts will create temporary `app.py` and `cdk.json` files during deployment and clean them up afterward.