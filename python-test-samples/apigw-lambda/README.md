[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
# Python Test Samples Project
This project contains automated test sample code samples for serverless applications written in Python. The project demonstrates several techniques for executing tests including mocking, emulation and testing in the cloud. Based on current tooling, we recommend customers **focus on testing in the cloud** as much as possible. 

## Testing in the Cloud
While testing in the cloud may create additional developer latency, increase costs, and require some customers to invest in additional dev-ops controls, this technique provides the most reliable, accurate, and complete test coverage. Performing tests in the context of the cloud allows you to test IAM policies, service configurations, quotas, and the most up to date API signatures and return values. Tests run in the cloud are most likely to produce consistent results as your code is promoted from environment to environment.

## Project contents
The project uses the [AWS Serverless Application Model](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) (SAM) CLI for configuration, testing and deployment. 

- [Python Test Samples Project](#python-test-samples-project)
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

This application creates several AWS resources, including a Lambda function and an API Gateway. These resources are defined in the `template.yaml` file in this project. This project includes the following files and folders:

- src - Code for the application's Lambda function.
- events - synthetic events that you can use to invoke the function.
- tests - Unit and integration tests for the application code. 
- template.yaml - A template that defines the application's AWS resources.

## Prerequisites
The SAM CLI is an extension of the AWS CLI that adds functionality for building and testing serverless applications. It contains features for building your appcation locally, deploying it to AWS, and emulating AWS services locally to support automated unit tests.  

To use the SAM CLI, you need the following tools.

* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* Python 3 - [Install Python 3](https://www.python.org/downloads/)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

[[top]](#apigw-lambda)

## Build and deploy with the SAM CLI
Use the following command to build your application locally: 

```bash
# build your application locally using a container
apigw-lambda$ sam build --use-container
```
The SAM CLI installs dependencies defined in `src/requirements.txt`, creates a deployment package, and saves it in the `.aws-sam/build` folder. [Read the documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-building.html).

Use the following command to deploy your application package to AWS: 

``` bash
# deploy your application to the AWS cloud 
apigw-lambda$ sam deploy --guided
```

After running this command you will receive a series of prompts:

* **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, and a good starting point would be something matching your project name. Use `apigw-lambda` as the stack name for this project.
* **AWS Region**: The AWS region you want to deploy your app to.
* **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review. If set to no, the AWS SAM CLI will automatically deploy application changes.
* **Allow SAM CLI IAM role creation**: Many AWS SAM templates, including this example, create AWS IAM roles required for the AWS Lambda function(s) included to access AWS services. By default, these are scoped down to minimum required permissions. To deploy an AWS CloudFormation stack which creates or modifies IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be provided. If permission isn't provided through this prompt, to deploy this example you must explicitly pass `--capabilities CAPABILITY_IAM` to the `sam deploy` command.
* **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.

You can find your API Gateway Endpoint URL in the output values displayed after deployment. Take note of this URL for use in the logging section below. On subsequent deploys you can run `sam deploy` without the `--guided` flag. [Read the documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-deploying.html).

[[top]](#apigw-lambda)

## Working with events
Testing event driven architectures often requires working with synthetic events. Events are frequently defined as JSON documents. Synthetic events are test data that represent AWS events such as a requests from API Gateway or a messages from SQS. 

AWS Lambda always requires an event during invocation. A sample test event is included in the `events` folder in this project. SAM provides the capability of generating additional synthetic events for a variety of AWS services. [Read the documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-local-generate-event.html).

Use the following command to learn more about generating synthetic events:
```bash
# generate a synthetic event
apigw-lambda$ sam local generate-event
```
[[top]](#apigw-lambda)

## Working with local emulators
Local emulation of AWS services offers a simple way to build and test cloud native applications using local resources. Local emulation can speed up the build and deploy cycle creating faster feedback loops for application developers. 

Local emulation has several limitations. Cloud services evolve rapidly, so local emulators are unlikely to have feature parity with their counterpart services in the cloud. Local emulators may not be able to provide an accurate representation of IAM permissions or service quotas. Local emulators do not exist for every AWS service.

SAM provides local emulation features for [AWS Lambda](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-invoke.html) and [Amazon API Gateway](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-start-api.html). AWS provides [Amazon DynamoDB Local](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html) as well as [AWS Step Functions Local](https://docs.aws.amazon.com/step-functions/latest/dg/sfn-local.html). Third party vendors like [LocalStack](https://docs.localstack.cloud/overview/) may provide emulation for additional AWS services. 

This project demonstrates local emulation of Lambda and API Gateway with SAM.

[[top]](#apigw-lambda)

## Use the SAM Lambda emulator 
The SAM CLI can emulate a Lambda function inside a Docker container deployed to your local desktop. To use this feature, invoke the function with the `sam local invoke` command passing a synthetic event. Print statements log to standard out. [Read the documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-invoke.html).

```bash
# invoke a Lambda function locally
apigw-lambda$ sam local invoke PythonTestDemo --event events/event.json
```

The `sam local start-lambda` command starts a local endpoint that emulates the AWS Lambda invoke endpoint. You can invoke it from your automated tests. Because this endpoint emulates the AWS Lambda invoke endpoint, you can write tests and then run them against the local Lambda emulator. You can also run the same tests against a deployed AWS SAM stack in your CI/CD pipeline. [Read the documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-automated-tests.html).

```bash
# start a local emulator for a Lambda function endpoint
apigw-lambda$ sam local start-lambda --region us-east-1
```

```bash
# run a unit test in a separate terminal
apigw-lambda$ python3 -m pytest -s tests/unit/local_emulator_test.py -v
```
[[top]](#apigw-lambda)

## Use the SAM API Gateway emulator
The SAM CLI can also emulate your application's API. Use the `sam local start-api` to run the API locally on port 3000.

```bash
# start a local emulator for an API Gateway endpoint
apigw-lambda$ sam local start-api
```

```bash
# make a request to the endpoint in a separate terminal
apigw-lambda$ curl http://localhost:3000/hello
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
[[top]](#apigw-lambda)

## Run a unit test using a mock framework
Lambda functions frequently call other AWS or 3rd party services. Mock frameworks are useful to simulate service responses. Mock frameworks can speed the development process by enabling rapid feedback iterations. Mocks can be particularly useful for testing failure cases when testing these branches of logic are difficult to do in the cloud.

This project uses mocks to test the internal logic of a Lambda function. 
The project uses the [moto](http://docs.getmoto.org/en/latest/) dependency library to mock an external service call to Amazon S3. The `moto` library can simulate responses from a variety of [AWS services](http://docs.getmoto.org/en/latest/docs/services/index.html). Tests with mocks are defined in the `tests/unit` folder. Use `pip` to install test dependencies and `pytest` to run the unit test.

```bash
# Create and Activate a Python Virtual Environment
apigw-lambda$ pip3 install virtualenv
apigw-lambda$ python3 -m venv venv
apigw-lambda$ source ./venv/bin/activate

# install dependencies
apigw-lambda$ pip3 install -r tests/requirements.txt

# run unit tests with mocks
apigw-lambda$ python3 -m pytest -s tests/unit/mock_test.py -v
```
[[top]](#apigw-lambda)

## Run integration tests against cloud resources
Integration tests run against deployed cloud resources. Since local unit tests cannot adequately test IAM permissions, our integration tests confirm that permissions are properly configured. Run integration tests against your deployed cloud resources with the following command:

```bash
# Set the environment variable AWS_SAM_STACK_NAME to the name of the stack you specified during deploy
apigw-lambda$ AWS_SAM_STACK_NAME=<stack-name> python3 -m pytest -s tests/integration -v
```
[[top]](#apigw-lambda)

## Invoke a Lambda function in the cloud
The `AWS CLI` enables you to invoke a Lambda function in the cloud.

```bash
# invoke a Lambda function in the cloud using the AWS CLI.  Substitute the function name as created in your stack.
aws lambda invoke --function-name apigw-lambda-PythonTestDemo-6Ecinx8IauZv outfile.txt
```
[[top]](#apigw-lambda)

## Fetch, tail, and filter Lambda function logs locally
To simplify troubleshooting, SAM CLI has a command called `sam logs`. The `sam logs` command lets you fetch logs generated by your deployed Lambda function from the command line. In addition to printing the logs on the terminal, this command has several features to help you quickly find your bug.

`NOTE`: This command works for all AWS Lambda functions; not just the ones you deploy using SAM.

```bash
apigw-lambda$ sam logs -n PythonTestDemo --stack-name apigw-lambda --tail
```

In a new terminal, curl the API Gateway and watch the log output.

```bash
apigw-lambda$ curl <API Gateway url>
```

You can find more information and examples about filtering Lambda function logs in the [SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-logging.html).

[[top]](#apigw-lambda)

## Use SAM Accerate to speed up feedback cycles
AWS SAM Accelerate is a set of features that reduces deployment latency and enable developers to test their code quickly against production AWS services in the cloud.
[Read the blog post](https://aws.amazon.com/blogs/compute/accelerating-serverless-development-with-aws-sam-accelerate/)

```bash
# synchronize local code with the cloud
apigw-lambda$ sam sync --watch --stack-name apigw-lambda
```

AWS Cloud Development Kit (CDK) has a similar synchronization feature, `cdk watch`. To learn more about `cdk watch` read this [blog post](https://aws.amazon.com/blogs/developer/increasing-development-speed-with-cdk-watch/). 

[[top]](#apigw-lambda)

## Implement application tracing
You can use AWS X-Ray to track user requests as they travel through your entire application. With X-Ray, you can understand how your application and its underlying services are performing to identify and troubleshoot the root cause of performance issues and errors.

This [Lambda function](./src/app.py) handler has been instrumented using AWS X-Ray. Find to your Lambda function in the console. Then navigate to `Monitor` -> `Traces` and you should see a graph of your X-Ray trace.

You may also navigate to the [X-Ray service](https://console.aws.amazon.com/xray/home) in the console to examine your traces in greater detail. In the console you should be able to find a service map that looks similar to the one below. 

![X-Ray image](./img/xray.png)

[[top]](#apigw-lambda)

## Perform a load test
Load tests should be executed in the cloud prior to any initial deployment to production environments. Load tests can be useful to discover performance bottlenecks and quota limits. Load tests should be scripted and repeatable. Load tests should simulate your application's expected peak load + 10% or more.

[Locust](https://locust.io/) is a Python-based open source load testing tool. To learn more about how to use Locust to load test your application see this [sample project](https://github.com/aws-samples/cdk-deployment-of-locust).

[[top]](#apigw-lambda)

## Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
aws cloudformation delete-stack --stack-name apigw-lambda
```

## Additional Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

Check out [serverlessland.com](https://serverlessland.com/) to view the latest blogs, videos and training for AWS Serverless. 
