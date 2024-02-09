# Springboot with DynamoDB Application
Synchronous sample Spring boot application written in Java which performs customer CRUD operations. AWS serverless services like Amazon API Gateway, ALB, ECR, Fargate, DynamoDB & SQS being used to host and test the application flow.
Java application is containerized & docker image pushed to ECR. Application is deployed into Fargate & endpoints are available through Application load balancer. API endpoints are set in API Gateway. CRUD operations are invoked via API Gateway which invokes API endpoints of application. Customer details sent to API requests are stored into DynamoDB tables as well as accessed as per the CRUD operations. Finally, post Deployment event placed into SQS.

![customer_crud_app.png](doc%2Fcustomer_crud_app.png)

### Application
Java17 maven application with Springboot 2.2.6 and AWS Java SDK 1.11.614 dependencies.

### Pre-requisites
1) SQS Queue
2) DynamoDB tables

### Note
Once the application starts, we will trigger a message {"application_status":"ready"} will be dropped to the SQS

_________________________________________________________________________________________________________
## Integration Testing:

Serverless Application Development Approach:
The development of each application is based on AWS serverless Architecture. All Microservices are running in ECS Cluster as Fargate Containers. As part of micro service deployment template, required CPU core, memory, number of containers and auto scaling configuration are defined and same is provisioned during deployment. Each micro service container is associated with an ingress container which act as application load balancer.

![AWS_Lambda.png](doc%2FAWS_Lambda.png)

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

### Steps to follow in PyTest-Python:
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

_________________________________________________________________________________________________________

## Load Testing

Load Testing focuses on enabling serverless load testing using Artillery, a modern, powerful, and easy-to-use load testing toolkit. With this solution, you can simulate realistic traffic to your serverless applications, helping you identify performance bottlenecks, optimize resource allocation, and ensure the scalability of your serverless architecture.

### Prerequisites
Before you begin, ensure you have the following prerequisites:

1. Node.js and NPM should be pre-installed
2. AWS account (if using AWS Lambda)
3. Artillery installed globally (npm install -g artillery)

### Steps to execute Load Test
1. Create YAML test script files and define different sections    like load phases, target endpoints and scenario configurations
2. Open command prompt and execute the YAML file from the repository where its placed.Create output file before test run
3. Upon test completion open the output file through any browser chrome, firefox and view the results . When executed from AWS codebuild we can view the results directly in S3  b   bucket after test completes 
