"""
Metadata Validation 

This script validates the metadata for presenting the code sample on serverlessland.com.
It is used in a github action to verify the proper file format for 
     {language-test-samples}/{sub-project}/metadata.json

The script is called with the {language-test-samples}/{sub-project} as the only arguement

Example (from serverless-test-samples):

python3 .github/METADATA/metadata_json_validator.py python-test-samples/apigw-lambda

"""

from os import path
import re
import json
from github import Github, Auth
import sys

from aws_lambda_powertools.utilities.validation import validate

import os

FOLDERS_TO_IGNORE = ['img']


def get_list_of_changed_test_sample_directories(changed_files: str) -> set[str]:
    """
    From the list of files changed in git, extract unique test sample directories
    :param: changed_files - Comma separated list of files which have changed
    :return: a set of folder names which should contain valid metadata.json files
    """
    file_list = changed_files.split(",")

    folders = []
    for file in file_list:
        if re.match(r"^\w+-test-samples/[^/]+/.*", file):
            res = re.search(r"(^\w+-test-samples/[^/]+/).*", file)
            # folder_name: 'dotnet-test-samples/apigw-lambda'
            folder_name = res.group(1)

            res = re.search(r"^\w+-test-samples/([^/]+)/.*", file)
            # subfolder_name: 'apigw-lambda'
            subfolder_name = res.group(1)
            if subfolder_name not in FOLDERS_TO_IGNORE:
                folders.append(folder_name)

    return set(folders)

def github_pull_request_comment(comment: str):
    # Fetch the GitHub Automation flag from the GH_AUTOMATION enviroment variable
    github_automation = os.environ.get('GITHUB_AUTOMATION')
    if github_automation is not None and len(github_automation) > 0:

        # Fetch the Github Owner & Repo
        github_repository = os.environ.get('GITHUB_REPOSITORY')
        if github_repository is None or len(github_repository) == 0:
            print("GITHUB_REPOSITORY environment variable not set")
            sys.exit(2)

        [owner, repo] = github_repository.split('/')

        # Fetch the pull request number from the PR_NUMBER enviroment variable
        pr_number = os.environ.get('PR_NUMBER')
        if pr_number is None or len(pr_number) == 0:
            print("PR_NUMBER environment variable not set. Should be the pull request number")
            sys.exit(3)

        # Fetch the Github Token from the GITHUB_TOKEN enviroment variable
        github_token = os.environ.get('GITHUB_TOKEN')
        if github_token is None or len(github_token) == 0:
            print("GITHUB_TOKEN environment variable not set")
            sys.exit(4)

        github = Github(github_token)
        repo = github.get_repo(f"{owner}/{repo}")
        pr = repo.get_pull(pr_number)
        pr.create_issue_comment(comment)
        github.close()


def validate_metadata_json(metadata_schema: dict, metadata_json_filename: str) -> bool:
    """
    Validate a metadata.json file
    :param: metadata_schema - the metadata schema as a JSON string
    :param: metadata_json_filename - path to the metadata.json file to validate
    :return: Boolean indicating whether file was validated correctly
    """
    try:
        if not path.isfile(metadata_json_filename):
            raise FileNotFoundError(f"{metadata_json_filename} does not exist - please create it")

        with open(metadata_json_filename, "r", encoding="utf-8") as metadata_object:
            metadata_contents = json.load(metadata_object)

        validate(event=metadata_contents, schema=metadata_schema)

        diagram_path = path.dirname(metadata_json_filename) + metadata_contents["diagram"]
        if path.isfile(diagram_path) is False:
            raise FileNotFoundError("Invalid diagram path: " + metadata_contents["diagram"])

        for pattern_detail in metadata_contents["pattern_detail_tabs"]:
            detail_path = path.dirname(metadata_json_filename) + pattern_detail["filepath"]
            if not re.match(r"^http", detail_path):
                # Not checking links to external repos
                continue
            if path.isfile(detail_path) is False:
                raise FileNotFoundError("Invalid filepath path: " + pattern_detail["filepath"])

        return True
    except Exception as exception:
        print(f"Error in {metadata_json_filename}: {str(exception)}")
        github_pull_request_comment(f"Error in {metadata_json_filename}: {str(exception)}")
        return False

def validate_test_sample_folders(folders: set) -> bool:
    """
    Validate all changed test sample folders
    :param: pr_number - the pull request number
    :param: gh_automation - the GitHub Automation flag
    :param: folders - a set of folder names which should contain valid metadata.json files
    :return: Boolean indicating whether all metadata files validated correctly
    """

    script_dir = path.dirname(path.abspath(__file__))
    file_path = path.join(script_dir, 'metadata_json_schema.json')

    with open(file_path, "r", encoding="utf-8") as metadata_schema_file:
        metadata_schema = json.load(metadata_schema_file)
        validated_ok = True
        for folder in folders:
            metadata_filename = path.join(folder, "metadata.json")

            if not validate_metadata_json(metadata_schema, metadata_filename):
                validated_ok = False

        return validated_ok


if __name__ == "__main__":

    # Fetch the comma separated list of files which have changed from the ALL_CHANGED_FILES environment variable
    changed_files = os.environ.get('ALL_CHANGED_FILES')
    if changed_files is None or len(changed_files) == 0:
        print("ALL_CHANGED_FILES environment variable not set. Should be a comma separated list of files which have changed")
        sys.exit(1)

    # Fetch a list of all test sample directories which have changed
    test_sample_folders = get_list_of_changed_test_sample_directories(changed_files)

    # Validate each metadata.json file in turn
    if not validate_test_sample_folders(test_sample_folders):
        sys.exit(5)
