# Deployment Guide

This guide covers everything you need to deploy and operate the CNS427 Task Management API, including prerequisites, AWS setup, deployment procedures, and troubleshooting.

## Table of Contents

- [Prerequisites](#prerequisites)
- [AWS Account Setup](#aws-account-setup)
- [Installation](#installation)
- [Deployment](#deployment)
- [Testing After Deployment](#testing-after-deployment)
- [Cleanup](#cleanup)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Tools

1. **Python 3.13+**
   ```bash
   python3 --version  # Should be 3.13 or higher
   ```

> **Note**:
It is common for Linux distros to use the executable name python3 for Python 3.x, and have python refer to a Python 2.x installation. Some distros have an optional package you can install that makes the python command refer to Python 3. 

2. **Poetry** (Python dependency management)
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   # Or via pip
   pip install poetry
   ```

3. **Node.js 18+** (required for AWS CDK)
   ```bash
   node --version  # Should be 18 or higher
   npm --version
   ```

4. **AWS CDK CLI**
   ```bash
   npm install -g aws-cdk
   cdk --version
   ```

5. **AWS CLI v2**
   ```bash
   # macOS
   brew install awscli
   
   # Linux
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   
   # Verify installation
   aws --version
   ```

6. **Docker** (required for CDK Lambda bundling)
   ```bash
   docker --version
   ```
   - Download from: https://www.docker.com/products/docker-desktop

### Docker Alternatives

CDK supports using alternative container runtimes through the `CDK_DOCKER` environment variable. This is useful if you prefer tools like **Finch** (AWS's open-source Docker alternative) or other OCI-compliant container runtimes.

**Using Finch:**

1. **Install Finch**
   ```bash
   # macOS (via Homebrew)
   brew install --cask finch
   
   # Or download from: https://github.com/runfinch/finch
   ```

2. **Initialize Finch**
   ```bash
   finch vm init
   finch vm start
   ```

3. **Configure CDK to use Finch**
   ```bash
   # Set for current session
   export CDK_DOCKER=finch
   
   # Or add to your shell profile (~/.zshrc, ~/.bashrc)
   echo 'export CDK_DOCKER=finch' >> ~/.zshrc
   source ~/.zshrc
   ```

4. **Verify Finch is working**
   ```bash
   finch version
   finch ps  # Should show running containers (if any)
   ```

**Using other container runtimes:**

You can use any OCI-compliant container runtime by setting `CDK_DOCKER`:

```bash
# Podman
export CDK_DOCKER=podman

# Rancher Desktop
export CDK_DOCKER=nerdctl

# Custom path
export CDK_DOCKER=/path/to/your/container-runtime
```

**Note:** The container runtime must support the same command-line interface as Docker (build, run, etc.) for CDK bundling to work correctly.

### ARM64 Lambda Architecture and Cross-Platform Building

This project deploys Lambda functions using **ARM64 architecture** (AWS Graviton2 processors) for better price-performance:
- **20% lower cost** compared to x86_64
- **Up to 34% better performance** for many workloads
- **Lower latency** and better energy efficiency

#### Building ARM64 on Different Platforms

**macOS (Apple Silicon - M1/M2/M3):**
- ✅ Native ARM64 support - no additional setup needed
- Docker builds ARM64 images natively

**macOS (Intel):**
- ✅ Docker Desktop includes QEMU and buildx pre-configured
- ARM64 builds work out of the box through emulation

**Linux x86_64 (EC2, Ubuntu, etc.):**
- ⚠️ Requires QEMU and Docker buildx for cross-compilation
- Follow the setup instructions below

#### Setting up ARM64 Cross-Compilation on Linux x86_64

If you're deploying from a Linux x86_64 machine (like an EC2 instance), you need to enable multi-platform builds:

**1. Verify QEMU (ARM64 emulator):**

```bash
# Verify QEMU is registered
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
```

**2. Enable Docker buildx:**

```bash
# Create a new builder instance
docker buildx create --name multiarch --driver docker-container --use

# Bootstrap the builder
docker buildx inspect --bootstrap

# Verify ARM64 support
docker buildx ls
# Should show: linux/amd64, linux/arm64, linux/arm/v7, etc.
```

**3. Test ARM64 build:**

```bash
# Test building an ARM64 image
docker buildx build --platform linux/arm64 -t test-arm64 .

# Or test with CDK synth
cdk synth
```

#### Alternative: Use x86_64 Architecture

If cross-compilation is problematic, you can change the Lambda architecture to x86_64:

**In `infrastructure/core/task_api_stack.py`:**

```python
# Change from:
architecture=lambda_.Architecture.ARM_64,

# To:
architecture=lambda_.Architecture.X86_64,
```

**Trade-offs:**
- ✅ No cross-compilation needed on x86_64 systems
- ✅ Simpler build process
- ❌ ~20% higher Lambda costs
- ❌ Slightly lower performance

#### Troubleshooting ARM64 Builds

**Error: "exec format error" or "cannot execute binary file"**
- QEMU is not installed or not registered
- Run: `docker run --rm --privileged multiarch/qemu-user-static --reset -p yes`

**Error: "multiple platforms feature is currently not supported"**
- Docker buildx is not enabled
- Follow the buildx setup steps above

**Slow builds on x86_64:**
- ARM64 emulation is slower than native builds
- Consider using an ARM64 build machine (like AWS Graviton EC2) for faster builds
- Or switch to x86_64 architecture if build speed is critical

## AWS Account Setup

### 1. AWS Account

You need an AWS account with appropriate permissions to create:
- Lambda functions
- DynamoDB tables
- API Gateway APIs
- EventBridge event buses and rules
- IAM roles and policies
- CloudWatch log groups

### 2. Configure AWS Credentials

Set up your AWS credentials using one of these methods:

**Option A: AWS CLI Configuration (Recommended)**
```bash
aws configure
# Enter your:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (e.g., us-west-2)
# - Default output format (json)
```

**Option B: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
export AWS_SESSION_TOKEN=your_session_token  # If using temporary credentials
export AWS_DEFAULT_REGION=us-west-2
```

**Option C: AWS SSO**
```bash
aws sso login --profile your-profile
export AWS_PROFILE=your-profile
```

### 3. Bootstrap CDK (First-time only)

If this is your first time using CDK in your AWS account/region:

```bash
cdk bootstrap aws://ACCOUNT-ID/REGION

# Example:
cdk bootstrap aws://123456789012/us-west-2
```

## Installation

1. **Clone the repository** (if not already done)
   ```bash
   git clone <repository-url>
   cd cns427-task-api
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Verify installation**
   ```bash
   poetry run validate-setup
   ```

## Security Checks (Optional but Recommended)

Before deploying, you can run CDK Nag security checks to validate your infrastructure against AWS best practices:

```bash
# Run security checks (will fail if violations found)
make cdk-nag

# Or generate a security report (non-blocking)
make cdk-nag-report
```

**What CDK Nag checks**:
- IAM policies and roles
- API Gateway configuration
- Lambda security settings
- Encryption and logging

**Current status**: ✅ All violations addressed (0 violations)

For detailed information about CDK Nag, see the [CDK Nag Guide](cdk-nag-guide.md).

## Deployment

> **Important:** This project has **two separate CDK applications**:
> 1. **Main Application** (required) - The Task API itself
> 2. **Test Harness** (optional) - Infrastructure for EventBridge integration testing
> 
> They must be deployed separately and cannot be deployed with a single `cdk deploy --all` command.

### Step 1: Deploy Main Application Stacks

Deploy the main application infrastructure (core + API + monitoring):

```bash
# Using Make (recommended)
make deploy

# Or using Poetry script
poetry run deploy

# Or using CDK directly from project root
poetry run cdk deploy --all
```

This deploys **three stacks** that together form the main application:
- **cns427-task-api-core**: Foundation resources (DynamoDB table, EventBridge bus, IAM roles, CloudWatch logs)
- **cns427-task-api-api**: Compute and API resources (Lambda functions, API Gateway, EventBridge rules)
- **cns427-task-api-monitoring**: Observability resources (CloudWatch dashboards and alarms)

**Note:** These stacks have dependencies (API depends on Core, Monitoring depends on API) and CDK deploys them in the correct order automatically.

### Step 2: Deploy Test Harness Stack (Optional)

The test harness is **optional** and only needed if you want to run EventBridge integration tests. It's a **separate CDK application** located in `infrastructure/test_harness/`.

Deploy the EventBridge testing infrastructure:

```bash
# Using Make (recommended)
make deploy-test-infra

# Or using CDK directly (must change directory)
cd infrastructure/test_harness
poetry run cdk deploy
cd ../..  # Return to project root
```

This deploys **one stack**:
- **cns427-task-api-test-harness**: Test infrastructure (DynamoDB table for test results, Lambda subscriber, EventBridge rule)

**Verify test infrastructure deployment:**
```bash
make check-test-infra
# Should output: ✅ Test infrastructure is deployed
```

**Why separate CDK apps?**
- Test infrastructure is optional (not needed for production)
- Keeps test resources isolated from production resources
- Allows independent lifecycle management
- Simpler to tear down test infrastructure without affecting main app

### Environment-Specific Deployments

**Development (default):**
```bash
poetry run cdk deploy --all
```

**Production:**
```bash
poetry run cdk deploy --all -c environment=prod -c project_name=cns427-task-api-prod
```

**Staging:**
```bash
poetry run cdk deploy --all -c environment=staging -c project_name=cns427-task-api-staging
```

**Custom Region:**
```bash
poetry run cdk deploy --all -c region=eu-west-1
```

### Deployment Output

After successful deployment, CDK will output:
- API Gateway endpoint URL
- Lambda function ARNs
- DynamoDB table names
- EventBridge bus ARN

Save these outputs for testing and verification.

## Testing After Deployment

### Unit Tests (No Deployment Required)

Unit tests can be run locally without any AWS infrastructure:

```bash
# Using Make
make test-unit

# Or using Poetry
poetry run test-unit
```

### Integration Tests (Requires Deployment)

**Important:** Integration, DynamoDB, and EventBridge tests require both core application and test harness infrastructure to be deployed first.

**Prerequisites:**
1. Deploy core application: `make deploy`
2. Deploy test harness: `make deploy-test-infra`
3. Verify test infrastructure: `make check-test-infra`

**Run Integration Tests:**
```bash
# DynamoDB integration tests
make test-integration
# Or: poetry run test-integration

# EventBridge integration tests
make test-eventbridge
# Or: poetry run test-eventbridge
```

### Run All Tests

```bash
# Using Make (runs unit + integration + eventbridge)
make test

# Or using Poetry
poetry run test-all
```

**Note:** This will fail if infrastructure is not deployed.

### Generate Coverage Report

```bash
make coverage
# View report at: htmlcov/all/index.html
```

## Cleanup

### Important: Deletion Order

> **Critical:** Because the main app and test harness are **separate CDK applications**, you **cannot** use `cdk destroy --all` to destroy everything. You must destroy them separately in the correct order.

**You must destroy the test harness stack BEFORE destroying the main application stacks.** The test harness has an EventBridge rule that references the core event bus. AWS will not allow you to delete an event bus with active rules attached.

### Recommended: Destroy Using Make

The Makefile handles the correct order:

```bash
# Step 1: Destroy test harness (if deployed)
make destroy-test-infra

# Step 2: Destroy main application
make destroy
```

### Manual Destruction (Correct Order)

If destroying manually, you **must** follow this order:

**Step 1: Destroy Test Infrastructure First**
```bash
# Change to test harness directory
cd infrastructure/test_harness

# Destroy test harness stack
poetry run cdk destroy --force

# Return to project root
cd ../..
```

**Step 2: Destroy Main Application Stacks**
```bash
# From project root
poetry run cdk destroy --all --force
```

### What Happens If You Destroy in Wrong Order?

If you try to destroy the main stacks before the test harness, you'll get an error:

```
Cannot delete event bus 'cns427-task-api-core-task-events' because it has rules attached
```

**Solution:** Destroy the test harness first, then retry destroying the main stacks.

### Why Can't `cdk destroy --all` Handle Both?

- The main app and test harness are **separate CDK applications** with different `app.py` files
- `cdk destroy --all` only sees stacks in the current CDK app
- From project root: only sees main app stacks (core, api, monitoring)
- From `infrastructure/test_harness/`: only sees test harness stack
- This separation is intentional to keep test infrastructure isolated

### Clean Build Artifacts

```bash
make clean
```

This removes:
- `.pytest_cache/`
- `htmlcov/`
- `.coverage`
- `cdk.out/`
- `.mypy_cache/`
- `.ruff_cache/`
- `.venv/`
- `__pycache__/` directories
- `*.pyc` files

## Troubleshooting

### Common Issues

#### 1. CDK Bootstrap Required

**Error:** `Policy contains a statement with one or more invalid principals`

**Solution:**
```bash
cdk bootstrap aws://ACCOUNT-ID/REGION
```

#### 2. Docker Not Running

**Error:** `Cannot connect to the Docker daemon`

**Solution:**
- Start Docker Desktop
- Verify: `docker ps`

#### 3. AWS Credentials Not Configured

**Error:** `Unable to locate credentials`

**Solution:**
```bash
aws configure
# Or set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

#### 4. Region Mismatch

**Error:** Resources not found in expected region

**Solution:**
- Check `cdk.json` context region setting
- Verify AWS CLI default region: `aws configure get region`
- Override at deployment: `poetry run cdk deploy -c region=us-west-2`

#### 5. Poetry Dependencies Not Installed

**Error:** `ModuleNotFoundError: No module named 'aws_cdk'`

**Solution:**
```bash
poetry install
```

#### 6. CDK Synthesis Fails

**Error:** `jsii.errors.JSIIError`

**Solution:**
- Check Python version: `python --version` (must be 3.13+)
- Reinstall dependencies: `poetry install --no-cache`
- Clear CDK cache: `rm -rf cdk.out/`

#### 7. Test Infrastructure Not Found

**Error:** `❌ Test infrastructure not found`

**Solution:**
```bash
make deploy-test-infra
```

#### 8. Lambda Function Timeout

**Error:** Task timed out after X seconds

**Solution:**
- Check CloudWatch logs: `aws logs tail /aws/lambda/cns427-task-api-task-handler --follow`
- Increase timeout in stack definition if needed

#### 9. DynamoDB Table Already Exists

**Error:** `Table already exists`

**Solution:**
- Use different project name: `poetry run cdk deploy -c project_name=my-unique-name`
- Or destroy existing stack first: `make destroy`

#### 10. EventBridge Events Not Captured

**Error:** Test events not appearing in test results table

**Solution:**
- Verify test infrastructure is deployed: `make check-test-infra`
- Check EventBridge rule is enabled:
  ```bash
  aws events describe-rule \
    --name cns427-task-api-test-rule \
    --event-bus-name cns427-task-api-core-task-events \
    --region us-west-2
  ```
- Check Lambda logs for errors:
  ```bash
  aws logs tail /aws/lambda/cns427-task-api-test-subscriber --follow
  ```

#### 11. Log Group Already Exists After CDK Changes

**Error:** `Resource of type 'AWS::Logs::LogGroup' with identifier '/aws/lambda/...' already exists`

**Why this happens:**

When you modify CDK code to change how log groups are created (e.g., switching from `log_retention` parameter to explicit `LogGroup` resources), CloudFormation tries to create a new log group with the same name that already exists from the previous deployment.

**Background:**

Originally, log groups were created implicitly using the `log_retention` parameter on Lambda functions. This approach was deprecated by AWS CDK. The modern approach is to create explicit `LogGroup` resources with a `retention` property. However, when you make this change, CloudFormation sees the explicit log group as a new resource and tries to create it, conflicting with the existing one.

**Solution:**

You need to manually delete the existing log groups before redeploying:

```bash
# 1. List all log groups for your project
aws logs describe-log-groups \
  --log-group-name-prefix /aws/lambda/cns427-task-api \
  --region us-west-2

# 2. Delete each log group manually
aws logs delete-log-group \
  --log-group-name /aws/lambda/cns427-task-api-task-handler \
  --region us-west-2

aws logs delete-log-group \
  --log-group-name /aws/lambda/cns427-task-api-notification-handler \
  --region us-west-2

aws logs delete-log-group \
  --log-group-name /aws/lambda/cns427-task-api-test-subscriber \
  --region us-west-2

# 3. Redeploy with the updated CDK code
make deploy
make deploy-test-infra
```

**Alternative (if you have many log groups):**

```bash
# Delete all log groups for your project at once
aws logs describe-log-groups \
  --log-group-name-prefix /aws/lambda/cns427-task-api \
  --region us-west-2 \
  --query 'logGroups[*].logGroupName' \
  --output text | \
  xargs -n 1 aws logs delete-log-group --log-group-name --region us-west-2
```

**Important:** This will delete your existing logs. If you need to preserve them, export them first:

```bash
# Export logs before deletion (optional)
aws logs create-export-task \
  --log-group-name /aws/lambda/cns427-task-api-task-handler \
  --from $(date -u -d '30 days ago' +%s)000 \
  --to $(date -u +%s)000 \
  --destination your-s3-bucket \
  --destination-prefix lambda-logs/
```

### Getting Help

- Check CloudWatch logs for Lambda errors
- Review CDK synthesis output: `poetry run cdk synth`
- Enable verbose logging: `poetry run cdk deploy --verbose`
- Check AWS service quotas in your account

### Useful Commands

```bash
# List all CDK stacks
poetry run cdk list

# Show differences before deployment
poetry run cdk diff

# Synthesize CloudFormation templates
poetry run cdk synth

# View CloudWatch logs
aws logs tail /aws/lambda/FUNCTION-NAME --follow

# Describe CloudFormation stack
aws cloudformation describe-stacks --stack-name STACK-NAME

# Check AWS service quotas
aws service-quotas list-service-quotas --service-code lambda
```

## Examples

### Example 1: Deploy to Multiple Environments

```bash
# Development
poetry run cdk deploy --all -c environment=dev

# Staging
poetry run cdk deploy --all -c environment=staging -c project_name=cns427-task-api-staging

# Production
poetry run cdk deploy --all -c environment=prod -c project_name=cns427-task-api-prod -c region=us-east-1
```

### Example 2: Custom Project Name

```bash
# Deploy with custom project name
poetry run cdk deploy --all -c project_name=my-company-task-api

# This creates resources like:
# - my-company-task-api-tasks (DynamoDB table)
# - my-company-task-api-task-handler (Lambda function)
# - my-company-task-api-core-task-events (EventBridge bus)
```

### Example 3: Multi-Region Deployment

```bash
# Deploy to us-west-2
poetry run cdk deploy --all -c region=us-west-2 -c project_name=task-api-west

# Deploy to eu-west-1
poetry run cdk deploy --all -c region=eu-west-1 -c project_name=task-api-eu
```

### Example 4: Development Workflow

```bash
# 1. Install dependencies
poetry install

# 2. Run unit tests locally (no deployment needed)
make test-unit

# 3. Deploy core application
make deploy

# 4. Deploy test infrastructure
make deploy-test-infra

# 5. Verify test infrastructure
make check-test-infra

# 6. Run integration tests (requires deployment)
make test-integration

# 7. Run EventBridge tests (requires deployment)
make test-eventbridge

# 8. Make code changes
# ... edit code ...

# 9. Run unit tests again
make test-unit

# 10. Deploy updates
make deploy

# 11. Run all tests
make test

# 12. Cleanup when done
make destroy-test-infra
make destroy
```

## Next Steps

- **[Configuration Guide](configuration.md)** - Learn about infrastructure configuration
- **[Testing Guide](testing-guide.md)** - Understand the testing strategy
- **[Architecture Guide](architecture.md)** - Deep dive into the architecture

## References

- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [AWS CLI Configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html)
