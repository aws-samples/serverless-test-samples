import requests
import yaml


def test_delete_user():
    logToUpload = {}
    with open("tests/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    URL = config["url"]
    try:
        # delete Operation
        deleteurl = URL+"customers?customerId=126"
        response_delete = requests.delete(deleteurl)
        assert response_delete.status_code == 200
        print(str(response_delete.text))

        logToUpload['deleteOperation'] = 'deleteOperation successful'
    except:
        logToUpload['Lambda failure'] = 'Lambda Failed'
        print("Lambda Failed")

    return logToUpload

if __name__ == "__main__":
    test_delete_user()