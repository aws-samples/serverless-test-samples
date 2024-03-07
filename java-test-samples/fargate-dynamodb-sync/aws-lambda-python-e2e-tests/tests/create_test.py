import yaml
import requests
import json

def test_create_new_user():
    logToUpload = {}
    with open("tests/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    URL = config["url"]
    try:
        # create Operation
        createurl = URL+"customers/"
        data = {
            "customerId": "126",
            "name": "abcde",
            "email": "abcde@abc.com"
        }
        response_create = requests.post(createurl, data=json.dumps(data),headers={"Content-Type": "application/json"})
        assert response_create.status_code == 200
        print(str(response_create.text))

        logToUpload['createOperation'] = 'createOperation successful'
    except:
        logToUpload['Lambda failure'] = 'Lambda Failed'
        print("Lambda Failed")

    return logToUpload

if __name__ == "__main__":
    test_create_new_user()