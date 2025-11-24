"""
Testing Scripts

Poetry-integrated commands for running different types of tests.
"""

import subprocess
import sys


def print_status(message: str) -> None:
    """Print status message in blue."""
    print(f'\033[0;34m[INFO]\033[0m {message}')


def print_success(message: str) -> None:
    """Print success message in green."""
    print(f'\033[0;32m[SUCCESS]\033[0m {message}')


def print_error(message: str) -> None:
    """Print error message in red."""
    print(f'\033[0;31m[ERROR]\033[0m {message}')


def run_pytest(args: list[str], description: str) -> bool:
    """Run pytest with given arguments.

    This function follows Python's recommended security practices for subprocess execution:

    1. Uses subprocess.run() with shell=False (REQUIRED for security)
       - Arguments are passed directly to the executable without shell interpretation
       - Prevents command injection even if arguments contain special characters
       - This is the approach recommended by Python documentation and OWASP

    2. Input validation as defense-in-depth
       - Validates arguments against shell metacharacters before execution
       - Provides an additional security layer beyond shell=False
       - Helps catch potential issues early with clear error messages

    References:
    - Python subprocess docs: https://docs.python.org/3/library/subprocess.html#security-considerations

    Args:
        args: List of pytest arguments (validated internally, only accepts safe paths and flags)
        description: Description of the test run

    Returns:
        True if tests passed, False otherwise
    """
    print_status(f'Running {description}...')

    # Validate arguments to prevent command injection
    # Only allow safe pytest arguments (paths, flags, no shell metacharacters)
    safe_args = []
    for arg in args:
        # Reject any arguments with shell metacharacters
        if any(char in arg for char in ['&', '|', ';', '`', '$', '(', ')', '<', '>', '\n', '\r']):
            print_error(f'Rejected unsafe argument: {arg}')
            return False
        safe_args.append(arg)

    # Build command as a list with validated arguments
    command = ['pytest'] + safe_args

    try:
        subprocess.run(command, check=True, shell=False)
        print_success(f'{description} completed successfully!')
        return True
    except subprocess.CalledProcessError as e:
        print_error(f'{description} failed with exit code {e.returncode}')
        return False


def run_unit_tests() -> None:
    """Run unit tests only."""
    args = ['tests/unit', '-v']

    success = run_pytest(args, 'unit tests')
    sys.exit(0 if success else 1)


def run_integration_tests() -> None:
    """Run all integration tests including EventBridge tests if infrastructure is available."""
    # Check if EventBridge test infrastructure is deployed
    from scripts.test_infrastructure import verify_deployment

    print_status('Checking EventBridge test infrastructure...')
    status = verify_deployment()
    eventbridge_available = all(status.values())

    if eventbridge_available:
        print_success('EventBridge test infrastructure is ready!')

        # Run all integration tests including EventBridge
        args = [
            'tests/integration',
            '-v',
        ]
        success = run_pytest(args, 'integration tests (including EventBridge)')
    else:
        missing_components = [name for name, deployed in status.items() if not deployed]
        print_status('EventBridge test infrastructure not fully deployed')
        print_status(f'Missing components: {", ".join(missing_components)}')
        print_status('Running DynamoDB integration tests only...')

        # Run only DynamoDB integration tests
        args = [
            'tests/integration',
            '-v',
            '--ignore=tests/integration/test_eventbridge_integration.py',
        ]
        success = run_pytest(args, 'integration tests (DynamoDB only)')

        print_status('\nTo run EventBridge tests, deploy test infrastructure:')
        print('  make deploy-test-infra')

    sys.exit(0 if success else 1)


def run_e2e_tests() -> None:
    """Run end-to-end tests."""
    print_status('Running end-to-end tests...')
    print_status('Note: E2E tests require deployed infrastructure')

    # Run E2E tests
    e2e_args = [
        'tests/e2e',
        '-v',
        '-s',  # Don't capture output for better debugging
    ]

    success = run_pytest(e2e_args, 'end-to-end tests')

    if success:
        print_success('E2E tests completed successfully!')
        sys.exit(0)
    else:
        print_error('E2E tests failed')
        sys.exit(1)


def run_all_tests() -> None:
    """Run all tests in sequence."""
    print_status('Running complete test suite...')

    # Run unit tests first
    unit_args = ['tests/unit', '-v']
    unit_success = run_pytest(unit_args, 'unit tests')

    # Check if EventBridge infrastructure is available
    from scripts.test_infrastructure import verify_deployment

    eventbridge_status = verify_deployment()
    eventbridge_available = all(eventbridge_status.values())

    integration_success = True
    if eventbridge_available:
        print_success('EventBridge test infrastructure detected!')

        # Run all integration tests including EventBridge
        integration_args = [
            'tests/integration',
            '-v',
        ]
        integration_success = run_pytest(integration_args, 'integration tests (including EventBridge)')
    else:
        print_status('EventBridge test infrastructure not available, running DynamoDB tests only')

        # Run only DynamoDB integration tests
        integration_args = [
            'tests/integration',
            '-v',
            '--ignore=tests/integration/test_eventbridge_integration.py',
        ]
        integration_success = run_pytest(integration_args, 'integration tests (DynamoDB only)')

        print_status('To run EventBridge tests, deploy test infrastructure:')
        print('  make deploy-test-infra')

    # Run E2E tests
    print_status('Running end-to-end tests...')
    e2e_args = [
        'tests/e2e',
        '-v',
        '-s',  # Don't capture output for better debugging
    ]
    e2e_success = run_pytest(e2e_args, 'end-to-end tests')

    # Summary
    print_status('\nTest Suite Summary:')
    print(f'  Unit Tests: {"✓" if unit_success else "✗"}')
    if eventbridge_available:
        print(f'  Integration Tests: {"✓" if integration_success else "✗"}')
    else:
        print(f'  Integration Tests (DynamoDB only): {"✓" if integration_success else "✗"}')
    print(f'  E2E Tests: {"✓" if e2e_success else "✗"}')

    overall_success = unit_success and integration_success and e2e_success

    if overall_success:
        print_success('All available tests completed successfully!')
        sys.exit(0)
    else:
        print_error('Some tests failed')
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'unit':
            run_unit_tests()
        elif command == 'integration':
            run_integration_tests()
        elif command == 'e2e':
            run_e2e_tests()
        elif command == 'all':
            run_all_tests()
        else:
            print_error(f'Unknown test command: {command}')
            sys.exit(1)
    else:
        run_all_tests()
