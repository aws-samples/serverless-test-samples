# Test Harness 

### Testing Approach:
1. Once the deployment is done successfully in ECS, there will be message sent to SNS topic. 
2. As part of Lambda project, SQS will be created and subscribes to SNS topic. 
3. Lambda has all required access policies to run the automation test scripts defined to test the serverless application. 
4. Once the execution is done, the html report will be generated and stored in S3 bucket for further validation. 

### Steps to follow for Lambda set-up
1.	Set-up SNS project
2.	Set-up Lambda Project
3.	Deploy the lambda & test scripts code every time new tests were added.
4.	Lambda deployment will deploy the latest automation tests in Lambda
5.	In continuous deployment tool set notification message to SNS post deployment

### Manual trigger in Lambda: 
    Once the latest tests are deployed, navigate to Lambda function in AWS console, and click the Run button.
### Auto trigger in Lambda: 
Since the SQS subscribed to SNS topic, whenever the deployment happens, the Lambda will trigger the automation tests to test the microservices. 

## Steps to follow in PyTest-Python:
1. Install any IDE (PyCharm, Intellij, Eclipse) that supports python programming language. For demonstration purpose we will be using Intellij IDEA 2023.1 Community Edition

2. Install the below plugins from the IntelliJ marketplace.
    •	Python Community Edition 
    •	Black Connect

3. Install the below python modules in the terminal with the given pip commands
    •	requests (command: pip install requests)
    •	pytest (command: pip install pytest)
    •	pytest -html (command: pip install pytest-html)
    •	deepdiff(command: pip install deepdiff)

4. Create a new project or get project from version control if project exists in the remote repositories like GitHub or bit bucket.

5. Inside the src folder add two packages as data and e2e_tests. Inside the data package create a python file with name fake_payload.py. We will be using this python file to get the environmental details to generate session and token details. create a function with getPayload name and create a dictionary with the required key value pairs and return that dictionary. We will be using this getPayload function in our test python files.

6. Inside the e2e_tests package creates a package as ExpectedJsonFiles and keep the expected Json files here.

7. Inside the e2e_tests package creates test python files with prefixing or suffixing with test i.e. test_or _test along with the test name. Inside the test class create function, include the session, token generation code, and send the GraphQL query as part of the request in the dictionary format. Compare the expected json and actual using deepdiff and print the result.
   
8. Run the below command to run the tests and generate html report
    pytest - -html=AutomationReport.html  --self-contained-html                     
