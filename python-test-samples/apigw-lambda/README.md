[![python: 3.9](https://img.shields.io/badge/Python-3.9-green)](https://img.shields.io/badge/Python-3.9-green)
[![AWS: Lambda](https://img.shields.io/badge/AWS-Lambda-blueviolet)](https://img.shields.io/badge/AWS-Lambda-blueviolet)
[![test: unit](https://img.shields.io/badge/Test-Unit-blue)](https://img.shields.io/badge/Test-Unit-blue)
[![test: integration](https://img.shields.io/badge/Test-Integration-yellow)](https://img.shields.io/badge/Test-Integration-yellow)
[![test: local](https://img.shields.io/badge/Test-Local-red)](https://img.shields.io/badge/Test-Local-red)

# Python Starter Project
This project contains automated test sample code samples for serverless applications written in Python. The project demonstrates several techniques for executing tests including mocking, emulation and testing in the cloud. 

## Testing in the Cloud
We recommend customers **focus on testing in the cloud** as much as possible.  While testing in the cloud may create additional developer latency, increase costs, and require some customers to invest in additional dev-ops controls, this technique provides the most reliable, accurate, and complete test coverage. Performing tests in the cloud allows you to test IAM policies, service configurations, quotas, and the most up-to-date API signatures and return values. Tests run in the cloud are most likely to produce consistent results as you promote your code from environment to environment.

## Project contents
The project uses the [AWS Serverless Application Model](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) (SAM) CLI for configuration, testing and deployment. 

- [Python Starter Project](#python-starter-project)
  - [Testing in the Cloud](#testing-in-the-cloud)
  - [Project contents](#project-contents)
  - [Prerequisites](#prerequisites)
  - [Build and deploy with the SAM CLI](#build-and-deploy-with-the-sam-cli)
  - [Working with events](#working-with-events)
  - [Working with local emulators](#working-with-local-emulators)
  - [Use the SAM Lambda emulator](#use-the-sam-lambda-emulator)
  - [Use the SAM API Gateway emulator](#use-the-sam-api-gateway-emulator)
  - [Run a unit test using a mock framework](#run-a-unit-test-using-a-mock-framework)
  - [Run integration tests against cloud resources](#run-integration-tests-against-cloud-resources)
  - [Invoke a Lambda function in the cloud](#invoke-a-lambda-function-in-the-cloud)
  - [Fetch, tail, and filter Lambda function logs locally](#fetch-tail-and-filter-lambda-function-logs-locally)
  - [Use SAM Accerate to speed up feedback cycles](#use-sam-accerate-to-speed-up-feedback-cycles)
  - [Implement application tracing](#implement-application-tracing)
  - [Perform a load test](#perform-a-load-test)
  - [Cleanup](#cleanup)
  - [Additional Resources](#additional-resources)

This application creates several AWS resources, including a Lambda function and an API Gateway. We defined these resources in the `template.yaml` file in this project. This project includes the following files and folders:

- src - Code for the application's Lambda function.
- events - synthetic events that you can use to invoke the function.
- tests - Unit and integration tests for the application code. 
- template.yaml - A template that defines the application's AWS resources.

## Prerequisites
The SAM CLI extends the AWS CLI that adds functionality for building and testing serverless applications. It contains features for building your application locally, deploying it to AWS, and emulating AWS services locally to support automated unit tests.  

To use the SAM CLI, you need the following tools.

* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* Python 3 - [Install Python 3](https://www.python.org/downloads/)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

[[top]](#python-test-samples-project)

## Build and deploy with the SAM CLI
Use the following command to build your application locally: 

```shell
# Run from the project directory serverless-test-samples/python-test-samples/apigw-lambda
# build your application

sam build
```
The SAM CLI installs dependencies defined in `src/requirements.txt`, creates a deployment package, and saves it in the `.aws-sam/build` folder. [Read the documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-building.html).

Use the following command to deploy your application package to AWS: 

```shell
# deploy your application to the AWS cloud 

sam deploy --guided
```

After running this command you will receive a series of prompts:

* **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, and a good starting point would be something matching your project name. Use `apigw-lambda` as the stack name for this project.
* **AWS Region**: The AWS region you want to deploy your app to.
* **Confirm changes before deploy**: If set to yes, SAM CLI shows you any change sets for manual review before deployment. If set to no, the AWS SAM CLI will automatically deploy application changes.
* **Allow SAM CLI IAM role creation**: Many AWS SAM templates, including this example, create AWS IAM roles required for the AWS Lambda function(s) included to access AWS services. By default, SAM CLI scopes these down to minimum required permissions. To deploy an AWS CloudFormation stack which creates or changes IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be provided. If you don't provide permission through this prompt, you must explicitly pass `--capabilities CAPABILITY_IAM` to the `sam deploy` command.
* **Disable rollback** 
* **PythonTestDemo may not have authorization defined, Is this okay?**:  The stack creates a publically available endpoint
* **Save arguments to samconfig.toml**: If set to yes, SAM CLI saves your choices to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.

You can find your API Gateway Endpoint URL in the output values displayed after deployment. Take note of this URL for use in the logging section below. On subsequent deploys you can run `sam deploy` without the `--guided` flag. [Read the documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-deploying.html).

[[top]](#python-test-samples-project)

## Working with events
Testing event driven architectures often requires working with synthetic events. Developers are often defining their Events as JSON documents. Synthetic events are test data that represent AWS events such as a requests from API Gateway or messages from SQS. 

AWS Lambda always requires an event during invocation. This project includes a sample test event in the `events` folder. SAM provides the capability of generating additional synthetic events for a variety of AWS services. [Read the documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-local-generate-event.html).

Use the following command to learn more about generating synthetic events:
```shell
# generate a synthetic event

sam local generate-event
```
[[top]](#python-test-samples-project)

## Working with local emulators
Local emulation of AWS services offers a simple way to build and test cloud native applications using local resources. Local emulation can speed up the build and deploy cycle, creating faster feedback loops for application developers. 

Local emulation has several limitations. Cloud services evolve rapidly, so local emulators are unlikely to have feature parity with their counterpart services in the cloud. Local emulators may not provide an accurate representation of IAM permissions or service quotas. Local emulators do not exist for every AWS service.

SAM provides local emulation features for [AWS Lambda](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-invoke.html) and [Amazon API Gateway](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-start-api.html). AWS provides [Amazon DynamoDB Local](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html) and [AWS Step Functions Local](https://docs.aws.amazon.com/step-functions/latest/dg/sfn-local.html). Third-party vendors like [LocalStack](https://docs.localstack.cloud/overview/) may provide emulation for additional AWS services. 

This project demonstrates local emulation of Lambda and API Gateway with SAM.

[[top]](#python-test-samples-project)

## Use the SAM Lambda emulator 
The SAM CLI can emulate a Lambda function inside a Docker container deployed to your local desktop. To use this feature, invoke the function with the `sam local invoke` command passing a synthetic event. Print statements log to standard out. [Read the documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-invoke.html).

```shell
# Run from the project directory serverless-test-samples/python-test-samples/apigw-lambda
# invoke a Lambda function locally

sam local invoke PythonTestDemo --event events/event.json
```

The `sam local start-lambda` command starts a local endpoint that emulates the AWS Lambda invoke endpoint. You can invoke it from your automated tests. Because this endpoint emulates the AWS Lambda invoke endpoint, you can write tests and then run them against the local Lambda emulator. You can also run the same tests against a deployed AWS SAM stack in your CI/CD pipeline. [Read the documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-automated-tests.html).

```shell
# start a local emulator for a Lambda function endpoint

sam local start-lambda --region us-east-1
```

```shell
# run a unit test in a separate terminal

python3 -m pytest -s tests/unit/local_emulator_test.py -v
```
[[top]](#python-test-samples-project)

## Use the SAM API Gateway emulator
The SAM CLI can also emulate your application's API. Use the `sam local start-api` to run the API locally on port 3000.

```shell
# Run from the project directory serverless-test-samples/python-test-samples/apigw-lambda
# start a local emulator for an API Gateway endpoint

sam local start-api
```

```shell
# make a request to the endpoint in a separate terminal

curl http://localhost:3000/hello
```

The SAM CLI reads the application template to determine the API's routes and the functions that they invoke. The `Events` property on each function's definition includes the route and method for each path.

```yaml
      Events:
        HelloWorld:
          Type: Api
          Properties:
            Path: /hello
            Method: get
```
[[top]](#python-test-samples-project)

## Run a unit test using a mock framework
Lambda functions frequently call other AWS or 3rd party services. Mock frameworks are useful in simulating service responses. Mock frameworks can speed the development process by enabling rapid feedback iterations. Mocks can be useful for testing failure cases when testing these branches of logic is difficult to do in the cloud.

This project uses mocks to test the internal logic of a Lambda function. 
The project uses the [moto](http://docs.getmoto.org/en/latest/) dependency library to mock an external service call to Amazon S3. The `moto` library can simulate responses from a variety of [AWS services](http://docs.getmoto.org/en/latest/docs/services/index.html). We defined tests with mocks in the `tests/unit` folder. Use `pip` to install test dependencies and `pytest` to run the unit test.

```shell

# Run from the project directory serverless-test-samples/python-test-samples/apigw-lambda
# Create and Activate a Python Virtual Environment

pip3 install virtualenv
python3 -m venv venv
source ./venv/bin/activate

# install dependencies

pip3 install -r tests/requirements.txt

# run unit tests with mocks

python3 -m pytest -s tests/unit/mock_test.py -v
```
[[top]](#python-test-samples-project)

## Run integration tests against cloud resources
Integration tests run against deployed cloud resources. Since local unit tests cannot adequately test IAM permissions, our integration tests confirm that permissions are properly configured. Run integration tests against your deployed cloud resources with the following command:

```shell
# Run from the project directory serverless-test-samples/python-test-samples/apigw-lambda
# Set the environment variable AWS_SAM_STACK_NAME to the name of the stack you specified during deploy

AWS_SAM_STACK_NAME=<stack-name> python3 -m pytest -s tests/integration -v
```
[[top]](#python-test-samples-project)

## Invoke a Lambda function in the cloud
The `AWS CLI` enables you to invoke a Lambda function in the cloud.

```shell
# invoke a Lambda function in the cloud using the AWS CLI.  Substitute the function name as created in your stack.

aws lambda invoke --function-name apigw-lambda-PythonTestDemo-6Ecinx8IauZv outfile.txt
```
[[top]](#python-test-samples-project)

## Fetch, tail, and filter Lambda function logs locally
To simplify troubleshooting, SAM CLI has a command called `sam logs`. The `sam logs` command lets you fetch logs generated by your deployed Lambda function from the command line. In addition to printing the logs on the terminal, this command has several features to help you quickly find your bug.

`NOTE`: This command works for all AWS Lambda functions; not just the ones you deploy using SAM.

```shell
sam logs -n PythonTestDemo --stack-name apigw-lambda --tail
```

In a new terminal, curl the API Gateway and watch the log output.

```shell
curl <API Gateway url>
```

You can find more information and examples about filtering Lambda function logs in the [SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-logging.html).

[[top]](#python-test-samples-project)

## Use SAM Accerate to speed up feedback cycles
AWS SAM Accelerate is a set of features that reduces deployment latency and enable developers to test their code quickly against production AWS services in the cloud.
[Read the blog post](https://aws.amazon.com/blogs/compute/accelerating-serverless-development-with-aws-sam-accelerate/)

```shell
# Run from the project directory serverless-test-samples/python-test-samples/apigw-lambda
# synchronize local code with the cloud

sam sync --watch --stack-name apigw-lambda
```

AWS Cloud Development Kit (CDK) has a similar synchronization feature, `cdk watch`. To learn more about `cdk watch` read this [blog post](https://aws.amazon.com/blogs/developer/increasing-development-speed-with-cdk-watch/). 

[[top]](#python-test-samples-project)

## Implement application tracing
You can use AWS X-Ray to track user requests as they travel through your entire application. With X-Ray, you can understand how your application and its underlying services are performing to identify and troubleshoot the root cause of performance issues and errors.

We instrumented the [Lambda function](./src/app.py) handler using AWS X-Ray. Find to your Lambda function in the console. Then navigate to `Monitor` -> `Traces` and you should see a graph of your X-Ray trace.

You may also navigate to the [X-Ray service](https://console.aws.amazon.com/xray/home) in the console to examine your traces in greater detail. In the console you should be able to find a service map that looks similar to the one below. 

![X-Ray image](./img/xray.png)

[[top]](#python-test-samples-project)

## Perform a load test
You should perform load tests in the cloud prior to any initial deployment to production environments. Load tests can be useful to discover performance bottlenecks and quota limits. You should create scripted and repeatable load tests. Load tests should simulate your application's expected peak load + 10% or more.

[Locust](https://locust.io/) is a Python-based open source load testing tool. To learn more about how to use Locust to load test your application, see this [sample project](https://github.com/aws-samples/cdk-deployment-of-locust).

[[top]](#python-test-samples-project)

## Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```shell
aws cloudformation delete-stack --stack-name apigw-lambda
```

## Additional Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

Check out [serverlessland.com](https://serverlessland.com/) to view the latest blogs, videos and training for AWS Serverless. 


