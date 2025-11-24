"""
Main Application Deployment Scripts

Poetry-integrated commands for deploying the main CNS427 Task API application.
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
    """Deploy the main CNS427 Task API application."""
    print_status('Deploying CNS427 Task API application...')

    # Check if we're in the correct directory
    if not Path('pyproject.toml').exists() or not Path('services').exists():
        print_error('Please run this command from the cns427-task-api root directory')
        sys.exit(1)

    try:
        # # Clean up CDK output and cache directories to prevent path length issues
        # print_status('Cleaning up CDK output and cache directories...')
        # import shutil
        
        # cleanup_dirs = ['cdk.out', '.mypy_cache', '.ruff_cache', '.pytest_cache']
        # for dir_name in cleanup_dirs:
        #     dir_path = Path(dir_name)
        #     if dir_path.exists():
        #         try:
        #             shutil.rmtree(dir_path)
        #             print_status(f'Removed {dir_name}/')
        #         except Exception as e:
        #             print_status(f'Could not remove {dir_name}/: {e}')
        
        # Run CDK deploy with outputs file
        # Using list form with shell=False for security
        subprocess.run(['cdk', 'deploy', '--all', '--outputs-file', 'cdk-outputs.json', '--require-approval', 'never'], check=True, shell=False)
        print_success('CNS427 Task API deployed successfully!')
        print_status('Stack outputs saved to: cdk-outputs.json')
    except subprocess.CalledProcessError as e:
        print_error(f'Deployment failed with exit code {e.returncode}')
        sys.exit(1)
    except FileNotFoundError:
        print_error('CDK not found. Please install AWS CDK:')
        print('  npm install -g aws-cdk')
        sys.exit(1)


if __name__ == '__main__':
    main()
