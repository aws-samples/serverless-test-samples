import requests
import yaml


def test_get_list_of_users():
    logToUpload = {}
    with open("tests/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    URL = config["url"]
    try:
        # read Operation
        readurl = URL+"customers?customerId=124"
        response_specific = requests.get(readurl)
        assert response_specific.status_code == 200
        print(str(response_specific.text))
        logToUpload['readOperation'] = 'readOperation successful'
    except:
        logToUpload['Lambda failure'] = 'Lambda Failed'
        print("Lambda Failed")

    return logToUpload

if __name__ == "__main__":
    test_get_list_of_users()