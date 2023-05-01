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
import json
import argparse
import jsonschema
from metadata_json_schema import METADATA


def validate_metadata_json(metadata_json_filename: str) -> dict:
    """
    Run Validations for the metadata schema
    :param: metadata_json_filename - relative path from the CWD to the metadata.json file to analyze
    :return: Dict with first error
    """
    try:

        schema_errors = []

        with open(metadata_json_filename,"r", encoding="utf-8") as metadata_object:
            metadata_contents = json.load(metadata_object)

        validator = jsonschema.Draft7Validator(METADATA)
        schema_errors = [x for x in validator.iter_errors(metadata_contents)] 

        diagram_path = path.dirname(metadata_json_filename) + metadata_contents["diagram"]
        if path.isfile(diagram_path) is False:
            schema_errors.append("Invalid diagram path: " + metadata_contents["diagram"])

        if "https://github.com/aws-samples/serverless-test-samples" in metadata_contents["git_repo_url"]:
            for pattern_detail in metadata_contents["pattern_detail_tabs"]:
                detail_path = path.dirname(metadata_json_filename) + pattern_detail["filepath"]
                if path.isfile(detail_path) is False:
                    schema_errors.append("Invalid detail path: " + pattern_detail["filepath"])
        else:
            print( "External repo detected, bypassing code path checks.")

        if len(schema_errors) > 0:
            return {"body": str(schema_errors), "statusCode": 406}
     
        return {"body": "OK", "statusCode": 200}
    
    except FileNotFoundError as exception:
        return {"body": str([exception.filename + " not found"]), "statusCode": 404}
    except Exception as exception:
        return {"body": str([exception]), "statusCode": 422}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='metadata_json_validator.py',
        description='Validate metadata.json for presenting the code sample on serverlessland.com.'
    )

    parser.add_argument('sub_repo_path',
                        type=str,
                        help="Path to the sub-repo from the project root." + \
                             "Example: python-test-samples/apigw-lambda'"
                        )
    args = parser.parse_args()

    metadata_filename = path.join(args.sub_repo_path, "metadata.json")
    print(f"Validating: {metadata_filename}")
    print(validate_metadata_json(metadata_filename))
