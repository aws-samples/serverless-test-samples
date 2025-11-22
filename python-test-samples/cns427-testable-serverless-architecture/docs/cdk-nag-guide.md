# CDK Nag Security Checks Guide

## Overview

This project uses [CDK Nag](https://github.com/cdklabs/cdk-nag) to validate infrastructure code against AWS security best practices. CDK Nag is integrated conditionally, so it doesn't slow down normal development but can be enabled for security reviews.

### Implementation Status

✅ **Complete** - CDK Nag is fully integrated and ready to use

**What was implemented**:
- Conditional CDK Nag in `app.py` (disabled by default)
- Makefile targets: `make cdk-nag` and `make cdk-nag-report`
- Stack-level suppressions for demo-appropriate violations
- Fixed IAM and API Gateway security issues
- Comprehensive documentation

**Current violations**: 0 (all addressed through fixes or documented suppressions)

## Quick Start

### Run Security Checks (Blocking)

```bash
make cdk-nag
```

This will:
- Run AwsSolutions security checks
- **Fail if violations are found**
- Display violations in the console
- Exit with non-zero code (suitable for CI/CD)

### Generate Security Report (Non-Blocking)

```bash
make cdk-nag-report
```

This will:
- Run AwsSolutions security checks
- Generate CSV and JSON reports
- **Not fail the build** (violations are reported only)
- Save reports to `cdk.out/` directory

### Run All Quality Checks

```bash
make check
```

This runs:
1. Linting (ruff)
2. Type checking (mypy)
3. CDK Nag security checks

## How It Works

### Conditional Activation

CDK Nag is **disabled by default** to keep development fast. It's enabled via environment variables:

```bash
# Enable CDK Nag
ENABLE_CDK_NAG=true cdk synth

# Enable CDK Nag + Reports
ENABLE_CDK_NAG=true CDK_NAG_REPORT=true cdk synth

# Or via CDK context
cdk synth -c enable-cdk-nag=true
```

### Normal Development (CDK Nag Disabled)

```bash
# These commands run WITHOUT CDK Nag (fast)
cdk synth
cdk deploy
make deploy
```

### Security Review (CDK Nag Enabled)

```bash
# These commands run WITH CDK Nag (thorough)
make cdk-nag
make cdk-nag-report
make check
```

## Understanding CDK Nag Output

### Violation Format

```
[Error] AwsSolutions-IAM4: The IAM user, role, or group uses AWS managed policies
  - Stack: cns427-task-api-core
  - Resource: LambdaExecutionRole/Resource
  - Severity: Medium
  - Recommendation: Use customer managed policies instead
```

### Severity Levels

- **Error**: Must be fixed or suppressed
- **Warning**: Should be reviewed
- **Info**: Informational only

## Common Violations and Fixes

### IAM4: AWS Managed Policies

**Violation**: Lambda uses AWS managed policy `AWSLambdaBasicExecutionRole`

**Fix Options**:
1. Create custom policy with only needed permissions
2. Suppress if AWS managed policy is acceptable for demo

### IAM5: Wildcard Permissions

**Violation**: IAM policy uses wildcard (`*`) in actions or resources

**Fix Options**:
1. Specify exact resources and actions
2. Suppress if wildcard is necessary (e.g., CloudWatch Logs)

### L1: Lambda Reserved Concurrency

**Violation**: Lambda function doesn't have reserved concurrency

**Fix Options**:
1. Set `reserved_concurrent_executions` in CDK
2. Suppress if using account-level limits

### DDB3: Point-in-Time Recovery

**Violation**: DynamoDB table doesn't have PITR enabled

**Fix**: Already enabled in our code ✅

## Suppressing Violations

If a violation is acceptable (e.g., for demo/educational purposes), you can suppress it:

### Stack-Level Suppression

```python
from cdk_nag import NagSuppressions

# In your stack
NagSuppressions.add_stack_suppressions(
    self,
    [
        {
            'id': 'AwsSolutions-IAM4',
            'reason': 'AWS managed policies acceptable for demo purposes'
        }
    ]
)
```

### Resource-Level Suppression

```python
NagSuppressions.add_resource_suppressions(
    lambda_function,
    [
        {
            'id': 'AwsSolutions-L1',
            'reason': 'Reserved concurrency not needed for demo workload'
        }
    ]
)
```

## Report Files

When you run `make cdk-nag-report`, reports are generated in `cdk.out/`:

### CSV Reports
- `AwsSolutions-cns427-task-api-core.csv`
- `AwsSolutions-cns427-task-api-api.csv`
- `AwsSolutions-cns427-task-api-monitoring.csv`

### JSON Reports
- `AwsSolutions-cns427-task-api-core.json`
- `AwsSolutions-cns427-task-api-api.json`
- `AwsSolutions-cns427-task-api-monitoring.json`

### Report Contents

Each report includes:
- Rule ID (e.g., AwsSolutions-IAM4)
- Resource path
- Compliance status
- Severity level
- Recommendation

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Run CDK Nag Security Checks
  run: make cdk-nag
  env:
    ENABLE_CDK_NAG: true
```

### GitLab CI Example

```yaml
cdk-nag:
  script:
    - make cdk-nag
  variables:
    ENABLE_CDK_NAG: "true"
```

## Rule Packs

Currently using: **AwsSolutions** (AWS Solutions best practices)

Other available rule packs:
- `HIPAASecurityChecks` - HIPAA compliance
- `NIST80053R5Checks` - NIST 800-53 Rev 5
- `PCIDSS321Checks` - PCI DSS 3.2.1

To change rule pack, edit `app.py`:

```python
from cdk_nag import HIPAASecurityChecks

cdk.Aspects.of(app).add(HIPAASecurityChecks(verbose=True))
```

## Best Practices

1. **Run before commits**: `make cdk-nag` before committing infrastructure changes
2. **Generate reports regularly**: Track security posture over time
3. **Document suppressions**: Always provide clear reasons for suppressions
4. **Review in PRs**: Include CDK Nag output in pull request reviews
5. **Enable in CI/CD**: Block deployments on security violations

## Troubleshooting

### CDK Nag Not Running

Check that it's enabled:
```bash
# Should see: "🔒 CDK Nag: Enabled"
ENABLE_CDK_NAG=true cdk synth
```

### Too Many Violations

Start with reports to understand scope:
```bash
make cdk-nag-report
# Review reports in cdk.out/
```

Then fix or suppress violations incrementally.

### Performance Issues

CDK Nag adds ~10-30 seconds to synth time. This is why it's disabled by default for development.

## Resources

- [CDK Nag GitHub](https://github.com/cdklabs/cdk-nag)
- [AwsSolutions Rules](https://github.com/cdklabs/cdk-nag/blob/main/RULES.md)
- [CDK Nag Workshop](https://catalog.workshops.aws/cdk-nag)
- [AWS Security Best Practices](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)

## Implementation Details

### Files Modified

1. **`app.py`** - Added conditional CDK Nag integration
   - Disabled by default (no performance impact)
   - Enable with `ENABLE_CDK_NAG=true`
   - Supports report generation with `CDK_NAG_REPORT=true`

2. **`Makefile`** - Added CDK Nag targets
   - `make cdk-nag` - Run security checks (blocking)
   - `make cdk-nag-report` - Generate reports (non-blocking)
   - `make check` - Now includes CDK Nag

3. **`infrastructure/core/task_api_stack.py`** - Security improvements
   - Replaced AWS managed policies with inline policies
   - Added API Gateway request validation
   - Added stack-level suppressions with justifications

### Suppressions

**Suppressed with Justification (8 violations)**:
1. ✅ **AwsSolutions-COG4** (×5) - Using IAM auth instead of Cognito (appropriate for demo)
   - IAM auth with SigV4 signing provides sufficient security
   - Cognito adds unnecessary complexity and cost for demo
2. ✅ **AwsSolutions-APIG1** (×1) - Access logging disabled (cost reduction for demo)
   - Lambda CloudWatch Logs provide sufficient observability
3. ✅ **AwsSolutions-APIG3** (×1) - WAF not configured (cost reduction for demo)
   - IAM auth already restricts access
   - WAF would add ~$5-10/month without substantial benefit for demo
4. ✅ **AwsSolutions-APIG6** (×1) - Stage logging disabled (Lambda logs sufficient for demo)
   - Lambda logs provide sufficient observability
   - Stage logging would duplicate information

All suppressions include detailed justifications and are documented in the code.

### Integration with Existing Workflow

**Before**:
```bash
make check  # lint + type-check
```

**After**:
```bash
make check  # lint + type-check + cdk-nag
```

CDK Nag is now part of your quality checks!

### Performance Impact

- **Normal development**: No impact (CDK Nag disabled by default)
- **Security checks**: Adds ~10-30 seconds to synth time
- **CI/CD**: One-time cost per pipeline run

### Testing the Implementation

```bash
# Test 1: Verify CDK Nag is disabled by default
cdk synth
# Should see: "ℹ️  CDK Nag: Disabled"

# Test 2: Verify CDK Nag can be enabled
ENABLE_CDK_NAG=true cdk synth
# Should see: "🔒 CDK Nag: Enabled"

# Test 3: Run security checks (should pass with 0 violations)
make cdk-nag

# Test 4: Generate reports
make cdk-nag-report
# Should create files in cdk.out/
```

---

**Status**: ✅ Implementation Complete - 0 violations  
**Next Steps**: Run `make cdk-nag` to verify security posture!
