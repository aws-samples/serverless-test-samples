"""
Main Application Destruction Scripts

Poetry-integrated commands for destroying the main CNS427 Task API application.
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


def print_error(message: str) -> None:
    """Print error message in red."""
    print(f'\033[0;31m[ERROR]\033[0m {message}')


def main() -> None:
    """Destroy the main CNS427 Task API application."""
    print_status('Destroying CNS427 Task API application...')

    # Check if we're in the correct directory
    if not Path('pyproject.toml').exists() or not Path('services').exists():
        print_error('Please run this command from the cns427-task-api root directory')
        sys.exit(1)

    # Confirm destruction
    response = input('Are you sure you want to destroy the CNS427 Task API application? (y/N): ')
    if response.lower() != 'y':
        print_status('Destruction cancelled.')
        return

    try:
        # Run CDK destroy
        # Using list form with shell=False for security
        # Note: This may take a minute as CDK synthesizes the stack before destroying
        print_status('Synthesizing stack (this may take a minute)...')
        subprocess.run(['cdk', 'destroy', '--all', '--force'], check=True, shell=False)
        print_success('CNS427 Task API destroyed successfully!')

        # Clean up any leftover CDK-generated log groups
        print_status('Cleaning up CDK-generated log groups...')
        try:
            # List all log groups with the project prefix
            result = subprocess.run(
                [
                    'aws',
                    'logs',
                    'describe-log-groups',
                    '--log-group-name-prefix',
                    '/aws/lambda/cns427-task-api',
                    '--query',
                    'logGroups[*].logGroupName',
                    '--output',
                    'text',
                ],
                capture_output=True,
                text=True,
                check=True,
                shell=False,
            )

            log_groups = result.stdout.strip().split()
            if log_groups and log_groups[0]:  # Check if any log groups exist
                for log_group in log_groups:
                    try:
                        subprocess.run(
                            ['aws', 'logs', 'delete-log-group', '--log-group-name', log_group, '--region', 'us-west-2'],
                            check=True,
                            shell=False,
                            capture_output=True,
                        )
                        print_status(f'Deleted log group: {log_group}')
                    except subprocess.CalledProcessError:
                        print_status(f'Could not delete log group: {log_group} (may not exist)')
            else:
                print_status('No leftover log groups found')
        except subprocess.CalledProcessError:
            print_status('Could not check for leftover log groups (AWS CLI may not be configured)')

    except subprocess.CalledProcessError as e:
        print_error(f'Destruction failed with exit code {e.returncode}')
        sys.exit(1)
    except FileNotFoundError:
        print_error('CDK not found. Please install AWS CDK:')
        print('  npm install -g aws-cdk')
        sys.exit(1)


if __name__ == '__main__':
    main()
