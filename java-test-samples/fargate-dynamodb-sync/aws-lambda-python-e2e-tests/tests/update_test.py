import requests
import json
import boto3
import yaml


def test_update_user():
    logToUpload = {}
    with open("tests/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    URL = config["url"]
    try:
        # update Operation
        updateurl = URL+"customers/"
        data = {
            "customerId": "127",
            "name": "test123",
            "email": "test@123.com"
        }
        response_update = requests.put(updateurl, data=json.dumps(data),headers={"Content-Type": "application/json"})
        assert response_update.status_code == 200
        print(str(response_update.text))

        logToUpload['updateOperation'] = 'updateOperation successful'
    except:
        logToUpload['Lambda failure'] = 'Lambda Failed'
        print("Lambda Failed")

    return logToUpload