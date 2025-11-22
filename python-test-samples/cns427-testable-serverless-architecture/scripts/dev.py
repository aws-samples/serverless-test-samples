"""
Development Scripts

Poetry-integrated commands for development tasks like linting, formatting, and type checking.
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


def run_command(command: list[str], description: str) -> bool:
    """Run a command and return success status.

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
        command: List of command arguments (validated for safety)
        description: Description of the command

    Returns:
        True if command succeeded, False otherwise
    """
    print_status(f'Running {description}...')

    # Validate command arguments to prevent injection
    # Only allow safe arguments (no shell metacharacters)
    for arg in command:
        if any(char in arg for char in ['&', '|', ';', '`', '$', '(', ')', '<', '>', '\n', '\r']):
            print_error(f'Rejected unsafe command argument: {arg}')
            return False

    try:
        # Explicitly disable shell for security
        subprocess.run(command, check=True, shell=False)
        print_success(f'{description} completed successfully!')
        return True
    except subprocess.CalledProcessError as e:
        print_error(f'{description} failed with exit code {e.returncode}')
        return False


def lint() -> None:
    """Run linting with ruff."""
    success = run_command(['ruff', 'check', '.'], 'linting')
    sys.exit(0 if success else 1)


def format() -> None:
    """Format code with ruff."""
    success = run_command(['ruff', 'format', '.'], 'code formatting')
    sys.exit(0 if success else 1)


def type_check() -> None:
    """Run type checking with mypy."""
    success = run_command(['mypy', 'services', 'shared'], 'type checking')
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'lint':
            lint()
        elif command == 'format':
            format()
        elif command == 'type-check':
            type_check()
        else:
            print_error(f'Unknown dev command: {command}')
            sys.exit(1)
    else:
        print_error('Please specify a dev command: lint, format, or type-check')
        sys.exit(1)
