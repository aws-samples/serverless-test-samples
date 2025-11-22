# CNS427 Task API - Makefile for test automation

.PHONY: help install test test-unit test-integration test-e2e test-all coverage lint format type-check cdk-nag cdk-nag-report check deploy deploy-test-infra destroy-test-infra check-test-infra clean

# Default target
help:
	@echo "CNS427 Task API - Available Commands:"
	@echo ""
	@echo "Setup:"
	@echo "  install              Install dependencies with Poetry"
	@echo "  validate-setup       Validate EventBridge testing setup"
	@echo ""
	@echo "Testing:"
	@echo "  test                 Run all available tests"
	@echo "  test-unit            Run unit tests only (fast, no AWS)"
	@echo "  test-property        Run property-based tests (Hypothesis, complex algorithms)"
	@echo "  test-integration     Run integration tests (includes EventBridge)"
	@echo "  test-e2e             Run end-to-end tests"
	@echo "  test-all             Run complete test suite"
	@echo "  coverage             Generate coverage report"
	@echo ""
	@echo "Test Infrastructure:"
	@echo "  deploy-test-infra    Deploy EventBridge test infrastructure"
	@echo "  destroy-test-infra   Destroy EventBridge test infrastructure"
	@echo "  check-test-infra     Check test infrastructure status"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint                 Run linting checks"
	@echo "  format               Format code with ruff"
	@echo "  type-check           Run type checking with mypy"
	@echo "  cdk-nag              Run CDK Nag security checks (blocks on violations)"
	@echo "  cdk-nag-report       Generate CDK Nag security report (non-blocking)"
	@echo "  check                Run all quality checks (lint + type-check + cdk-nag)"
	@echo ""
	@echo "Deployment:"
	@echo "  deploy               Deploy main application to AWS"
	@echo "  destroy              Destroy main application"
	@echo "  clean                Clean build artifacts"

# Setup
install:
	@echo "Installing dependencies..."
	poetry install

validate-setup:
	@echo "Validating EventBridge testing setup..."
	poetry run validate-setup

# Testing targets
test:
	@echo "Running all available tests..."
	poetry run test-all

test-unit:
	@echo "Running unit tests..."
	poetry run test-unit

test-property:
	@echo "Running property-based tests..."
	poetry run pytest tests/property_based/ -v

test-integration:
	@echo "Running integration tests (including EventBridge)..."
	poetry run test-integration

test-e2e:
	@echo "Running end-to-end tests..."
	poetry run test-e2e

test-all:
	@echo "Running complete test suite..."
	poetry run test-all

coverage:
	@echo "Generating coverage report..."
	poetry run pytest tests/ --cov=services --cov=shared --cov-report=html --cov-report=term
	@echo "Coverage report available at: htmlcov/index.html"

# Test Infrastructure Management
deploy-test-infra:
	@echo "Deploying EventBridge test infrastructure..."
	cd infrastructure/test_harness && poetry run cdk deploy
	
destroy-test-infra:
	@echo "Destroying EventBridge test infrastructure..."
	cd infrastructure/test_harness && poetry run cdk destroy

check-test-infra:
	@echo "Checking test infrastructure status..."
	@aws dynamodb describe-table --table-name cns427-task-api-test-results > /dev/null 2>&1 && echo "✅ Test infrastructure is deployed" || echo "❌ Test infrastructure not found"

# Code quality
lint:
	@echo "Running linting checks..."
	poetry run lint

format:
	@echo "Formatting code..."
	poetry run format

type-check:
	@echo "Running type checking..."
	poetry run type-check

cdk-nag:
	@echo "Running CDK Nag security checks..."
	@echo "This will fail if security violations are found."
	ENABLE_CDK_NAG=true poetry run cdk synth --quiet > /dev/null
	@echo "✅ CDK Nag checks passed - no security violations found"

cdk-nag-report:
	@echo "Generating CDK Nag security report..."
	ENABLE_CDK_NAG=true CDK_NAG_REPORT=true poetry run cdk synth --quiet > /dev/null
	@echo "✅ CDK Nag report generated"
	@echo "📊 Reports available at:"
	@echo "   - cdk.out/AwsSolutions-cns427-task-api-core.csv"
	@echo "   - cdk.out/AwsSolutions-cns427-task-api-api.csv"
	@echo "   - cdk.out/AwsSolutions-cns427-task-api-monitoring.csv"
	@echo "   - cdk.out/*.json (JSON format)"

check: lint type-check cdk-nag
	@echo "✅ All quality checks passed!"

# Deployment
deploy:
	@echo "Deploying main application to AWS..."
	poetry run deploy

destroy:
	@echo "Destroying main application..."
	poetry run destroy

# Cleanup
clean:
	@echo "Cleaning build artifacts..."
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf cdk.out/
	rm -rf infrastructure/test_harness/cdk.out/
	rm -rf cdk-outputs.json
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf .venv/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete