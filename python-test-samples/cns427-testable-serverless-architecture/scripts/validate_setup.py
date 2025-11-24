"""
Setup Validation Script

Validates that all Poetry commands and test infrastructure is working correctly.
"""

import subprocess
import sys
from pathlib import Path


def print_status(message: str) -> None:
    """Print status message in blue."""
    print(f'\033[0;34m[INFO]\033[0m {message}')


def print_success(message: str) -> None:
    """Print success message in green."""
    print(f'\033[0;32m[SUCCESS]\033[0m {message}')


def print_warning(message: str) -> None:
    """Print warning message in yellow."""
    print(f'\033[1;33m[WARNING]\033[0m {message}')


def print_error(message: str) -> None:
    """Print error message in red."""
    print(f'\033[0;31m[ERROR]\033[0m {message}')


def check_command_exists(command: str) -> bool:
    """Check if a command exists in PATH.

    Args:
        command: Command name to check (validated as single string)

    Returns:
        True if command exists, False otherwise
    """
    try:
        # Use list form with shell=False for security
        subprocess.run([command, '--version'], capture_output=True, check=True, shell=False)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_poetry_scripts() -> dict[str, bool]:
    """Check which Poetry scripts are defined in pyproject.toml.

    Returns:
        Dictionary mapping script names to availability (True if defined)
    """
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib

    try:
        with open('pyproject.toml', 'rb') as f:
            pyproject = tomllib.load(f)
        
        scripts = pyproject.get('tool', {}).get('poetry', {}).get('scripts', {})
        return {name: True for name in scripts.keys()}
    except Exception:
        return {}


def validate_setup() -> None:
    """Validate the complete project setup."""
    print_status('Validating project setup...')

    errors = []
    warnings = []

    # Check basic prerequisites
    print_status('Checking prerequisites...')

    if not Path('pyproject.toml').exists():
        errors.append('pyproject.toml not found - run from project root')
    else:
        print_success('✓ Project root directory')

    if not Path('services').exists():
        errors.append('services directory not found')
    else:
        print_success('✓ Services source code')

    if not Path('shared').exists():
        errors.append('shared directory not found')
    else:
        print_success('✓ Shared source code')

    # Check external dependencies
    if not check_command_exists('poetry'):
        errors.append('Poetry not installed')
    else:
        print_success('✓ Poetry installed')

    if not check_command_exists('cdk'):
        warnings.append('AWS CDK not installed - needed for infrastructure deployment')
    else:
        print_success('✓ AWS CDK installed')

    if not check_command_exists('aws'):
        warnings.append('AWS CLI not installed - needed for infrastructure management')
    else:
        print_success('✓ AWS CLI installed')

    # Check Poetry scripts
    print_status('Checking Poetry scripts...')

    available_scripts = check_poetry_scripts()
    
    # All Poetry scripts that should be defined (from Makefile targets that use poetry run)
    required_commands = [
        'validate-setup',
        'test-unit',
        'test-integration',
        'test-e2e',
        'test-all',
        'lint',
        'format',
        'type-check',
        'deploy',
        'destroy',
    ]

    for command in required_commands:
        if command in available_scripts:
            print_success(f'✓ poetry run {command}')
        else:
            errors.append(f'Poetry script not defined in pyproject.toml: {command}')
    
    # Check non-Poetry commands used by Makefile
    print_status('Checking additional tools...')
    
    optional_tools = [
        ('ruff', 'Code linting and formatting'),
        ('mypy', 'Type checking'),
        ('pytest', 'Test runner'),
    ]
    
    for tool, description in optional_tools:
        if check_command_exists(tool):
            print_success(f'✓ {tool} ({description})')
        else:
            warnings.append(f'{tool} not installed - {description}')
    
    # Note: cdk-nag is a Python package, not a CLI tool, so we don't check for it here
    # It's checked when running: ENABLE_CDK_NAG=true poetry run cdk synth

    # Check test directories
    print_status('Checking test structure...')

    test_dirs = [
        'tests/unit',
        'tests/unit/domain',
        'tests/unit/handlers',
        'tests/unit/models',
        'tests/integration',
        'tests/e2e',
        'tests/shared/fakes',
        'tests/shared/helpers',
    ]

    for test_dir in test_dirs:
        if Path(test_dir).exists():
            print_success(f'✓ {test_dir}/')
        else:
            errors.append(f'Test directory missing: {test_dir}')

    # Check key test files
    print_status('Checking key test files...')

    test_files = [
        'tests/unit/conftest.py',
        'tests/unit/domain/test_task_service.py',
        'tests/unit/handlers/test_task_handler.py',
        'tests/unit/models/test_event_contracts.py',
        'tests/integration/test_dynamodb_integration.py',
        'tests/integration/test_eventbridge_integration.py',
        'tests/e2e/test_task_lifecycle_e2e.py',
    ]

    for test_file in test_files:
        if Path(test_file).exists():
            print_success(f'✓ {test_file}')
        else:
            warnings.append(f'Test file missing: {test_file}')

    # Check infrastructure
    print_status('Checking infrastructure...')

    infra_paths = [
        ('infrastructure/core', 'Main infrastructure'),
        ('infrastructure/test_harness/app.py', 'Test harness'),
        ('infrastructure/setup.py', 'Infrastructure package'),
    ]

    for infra_path, description in infra_paths:
        if Path(infra_path).exists():
            print_success(f'✓ {description}: {infra_path}')
        else:
            warnings.append(f'{description} missing: {infra_path}')

    # Summary
    print_status('\nValidation Summary:')

    if errors:
        print_error(f'Found {len(errors)} errors:')
        for error in errors:
            print_error(f'  - {error}')

    if warnings:
        print_warning(f'Found {len(warnings)} warnings:')
        for warning in warnings:
            print_warning(f'  - {warning}')

    if not errors and not warnings:
        print_success('✓ All checks passed! Project setup is ready.')
    elif not errors:
        print_success('✓ Setup is functional with minor warnings.')
        print_status('\nYou can proceed with:')
        print('1. Run tests: poetry run test-all')
        print('2. Deploy application: poetry run deploy')
    else:
        print_error('✗ Setup has errors that need to be fixed before proceeding.')
        sys.exit(1)


if __name__ == '__main__':
    validate_setup()
