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
import argparse
import sys

from aws_lambda_powertools.utilities.validation import validate


def get_list_of_changed_test_sample_directories(changed_files: str) -> set[str]:
    """
    From the list of files changed in git, extract unique test sample directories which have a metadata.json file in them.

    There are a couple of edge cases.  Sometimes a directory doesn't contain a pattern (for instance /java-test-samples/img/)
    and sometimes the patterns are nested (for instance dotnet-test-samples/async-architectures/async-lambda-dynamodb)

    So as we can't reliably define whether the directory is a test sample directory,
    we instead just test whether a metadata.json file has changed.

    :param: changed_files - Comma separated list of files which have changed
    :return: a set of folder names which should contain valid metadata.json files
    """
    file_list = changed_files.split(",")

    folders = []
    for file in file_list:
        if re.match(r"^\w+-test-samples/[^/]+/.*", file):
            res = re.search(r"(^\w+-test-samples/.*/)metadata.json$", file)
            folders.append(res.group(1))

    return set(folders)


def validate_metadata_json(metadata_schema: dict, metadata_json_filename: str) -> bool:
    """
    Validate a metadata.json file
    :param: metadata_schema - the metadata schema as a JSON string
    :param: metadata_json_filename - path to the metadata.json file to validate
    :return: Boolean indicating whether file was validated correctly
    """
    try:

        with open(metadata_json_filename, "r", encoding="utf-8") as metadata_object:
            metadata_contents = json.load(metadata_object)

        validate(event=metadata_contents, schema=metadata_schema)

        diagram_path = path.dirname(metadata_json_filename) + metadata_contents["diagram"]
        if path.isfile(diagram_path) is False:
            raise FileNotFoundError("Invalid diagram path: " + metadata_contents["diagram"])

        for pattern_detail in metadata_contents["pattern_detail_tabs"]:
            detail_path = path.dirname(metadata_json_filename) + pattern_detail["filepath"]
            if path.isfile(detail_path) is False:
                raise FileNotFoundError("Invalid filepath path: " + pattern_detail["filepath"])

        return True
    except Exception as exception:
        print(str(exception))
        return False


def validate_test_sample_folders(folders: set) -> bool:
    """
    Validate all changed test sample folders
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

            print(f"Validating: {metadata_filename}")

            if not validate_metadata_json(metadata_schema, metadata_filename):
                validated_ok = False

        return validated_ok


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='metadata_json_validator.py',
        description='Validate metadata.json for presenting the code sample on serverlessland.com.'
    )

    parser.add_argument('changed_files',
                        type=str,
                        help="Path to the sub-repo from the project root." + \
                             "Example: python-test-samples/apigw-lambda'"
                        )
    args = parser.parse_args()

    # Fetch a list of all test sample directories which have changed
    test_sample_folders = get_list_of_changed_test_sample_directories(args.changed_files)

    # Validate each metadata.json file in turn
    if not validate_test_sample_folders(test_sample_folders):
        sys.exit(5)
