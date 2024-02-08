
# Overview


This GitHub project focuses on enabling serverless load testing using Artillery, a modern, powerful, and easy-to-use load testing toolkit. With this solution, you can simulate realistic traffic to your serverless applications, helping you identify performance bottlenecks, optimize resource allocation, and ensure the scalability of your serverless architecture.

# Features

1. Artillery itself is serverless which means it does not require any explicit server provisioning during load test execution. It creates all resources on demand needed to execute load test
2. We can generate multiple user load from a single machine itself using minimal resource usage also scalability is not an issue
3. Seemless integration with AWS and can run load tests in CI/CD pipeline using AWS code build

# Prerequisites

Before you begin, ensure you have the following prerequisites:

1. Node.js and NPM should be pre-installed
2. AWS account (if using AWS Lambda)
3. Artillery installed globally (npm install -g artillery)

# Steps To Execute Load Test Locally

1. Create YAML test script files and define different sections    like load phases, target endpoints and scenario configurations
2. Open command prompt and execute the YAML file from the repository where its placed. Create output file before test run
3. Upon test completion open the output file through any browser chrome, firefox and view the results.


# Steps To Execute Load Test In CI/CD Pipeline Using CodeBuild

1. Click on CodeBuild in AWS Console and create a build project
2. Create project configurations and connect to a source like github where Artillery code and buildspec file are located 
3. Choose environment which code build uses to run the build project
4. Create artifacts where test results get stored after test completion
5. Once build project is successfully created start the build, this way the test file will be executed 
6. Upon test completion results of the test can be viewed in S3 bucket 
7. View the cloudwatch metrics for details on the observability data