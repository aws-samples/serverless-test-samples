import requests
import json
import boto3
import create_test
import read_test
import delete_test
import update_test
import pytest
import os
import subprocess
 
print('Loading function')
s3 = boto3.client('s3')
s3_bucket = os.environ.get('S3_BUCKET', 'pocserverless-uc1')
report_name = 'pytest_report.html'
logToUpload = {}
 
def lambda_handler(event, context):
    logToUpload['GET'] = read_test.test_get_list_of_users()
    logToUpload['POST'] = create_test.test_create_new_user()
    logToUpload['DELETE'] = delete_test.test_delete_user()
    logToUpload['PUT'] = update_test.test_update_user()
 
    # Upload the result file into S3 bucket
    fileName = 'pocserverless_test_report' + '.json'
    uploadByteStream = bytes(json.dumps(logToUpload).encode('UTF-8'))
    s3.put_object(Bucket=s3_bucket, Key=fileName, Body=uploadByteStream)
    print('Put Complete') 
     
    # Generate HTML report
    subprocess.run(["/opt/python -m pytest --html=/var/lang/bin/report.html"], shell=True, capture_output=True, text=True)
    s3.upload_file('/var/lang/bin/report.html', s3_bucket, report_name)