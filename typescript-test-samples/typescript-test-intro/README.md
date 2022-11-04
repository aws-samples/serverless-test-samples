# Typescript Test Intro

This project contains automated test samples for serverless applications written in TypeScript. The project includes techniques for executing tests including mocking and testing in the cloud. Based on current tooling, we recommend customers **focus on testing in the cloud** as much as possible. 

## Testing in the Cloud

While testing in the cloud may create additional developer latency, increase costs, and require some customers to invest in additional dev-ops controls, this technique provides the most reliable, accurate, and complete test coverage. Performing tests in the context of the cloud allows you to test IAM policies, service configurations, quotas, and the most up to date API signatures and return values. Tests run in the cloud are most likely to produce consistent results as your code is promoted from environment to environment.

## Project contents

The project uses the [AWS Serverless Application Model](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) (SAM) CLI for configuration, testing and deployment. 

- [Project contents](#project-contents)
- [Prerequisites](#prerequisites)
- [Build and deploy with the SAM CLI](#build-and-deploy-with-the-sam-cli)
- [Working with events](#working-with-events)
- [Working with local emulators](#working-with-local-emulators)
- [Use the SAM API Gateway emulator](#use-the-sam-api-gateway-emulator)
- [Run a unit test using a mock framework](#run-a-unit-test-using-a-mock-framework)
- [Run integration tests against cloud resources](#run-integration-tests-against-cloud-resources)
- [Invoke a Lambda function in the cloud](#invoke-a-lambda-function-in-the-cloud)
- [Fetch, tail, and filter Lambda function logs locally](#fetch-tail-and-filter-lambda-function-logs-locally)
- [Use SAM Accerate to speed up feedback cycles](#use-sam-accerate-to-speed-up-feedback-cycles)
- [Implement application tracing](#implement-application-tracing)
- [Cleanup](#cleanup)
- [Additional Resources](#additional-resources)

This project contains source code and supporting files for a serverless application that you can deploy with the SAM CLI. It includes the following files and folders.

- [list-buckets](./list-buckets/) - Code for the application's Lambda function.
- [list-buckets/tests](./list-buckets/tests/) - [Unit](./list-buckets/tests/unit/) and [integration](./list-buckets/tests/integration/) tests for the application code. 
- [events](./events/) - synthetic events that you can use to invoke the function.
- [template.yaml](./template.yaml) - A template that defines the application's AWS resources.

The application uses several AWS resources, including Lambda functions and an API Gateway API. These resources are defined in the [template.yaml](./template.yaml) file in this project. You can update the template to add AWS resources through the same deployment process that updates your application code.

## Prerequisites

The SAM CLI is an extension of the AWS CLI that adds functionality for building and testing serverless applications. It contains features for building your appcation locally, deploying it to AWS, and emulating AWS services locally to support automated unit tests.  

To use the SAM CLI, you need the following tools.

* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* Python 3 - [Install Python 3](https://www.python.org/downloads/)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

[[top]](#typescript-test-intro)

## Build and deploy with the SAM CLI

Use the following command to build your application locally: 

```bash
# build your application locally
typescript-test-intro$ sam build
```
The SAM CLI installs dependencies defined in `list-buckets/package.json`, creates a deployment package, and saves it in the `.aws-sam/build` folder. [Read the documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-building.html).

Use the following command to deploy your application package to AWS: 

``` bash
# deploy your application to the AWS cloud 
typescript-test-intro$ sam deploy --guided
```

The second command will package and deploy your application to AWS, with a series of prompts:

* **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, and a good starting point would be something matching your project name.
* **AWS Region**: The AWS region you want to deploy your app to.
* **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review. If set to no, the AWS SAM CLI will automatically deploy application changes.
* **Allow SAM CLI IAM role creation**: Many AWS SAM templates, including this example, create AWS IAM roles required for the AWS Lambda function(s) included to access AWS services. By default, these are scoped down to minimum required permissions. To deploy an AWS CloudFormation stack which creates or modifies IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be provided. If permission isn't provided through this prompt, to deploy this example you must explicitly pass `--capabilities CAPABILITY_IAM` to the `sam deploy` command.
* **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.

You can find your API Gateway Endpoint URL in the output values displayed after deployment. Take note of this URL for use in the [integration testing section](run-integration-tests-against-cloud-resources) below. On subsequent deploys you can run `sam deploy` without the `--guided` flag. [Read the documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-deploying.html).

[[top]](#typescript-test-intro)

## Working with events

Testing event driven architectures often requires working with synthetic events. Events are frequently defined as JSON documents. Synthetic events are test data that represent the payloads AWS sends between service integrations, such as a requests from API Gateway or a messages from SQS.

AWS Lambda always requires an event during invocation. A sample test event is included in the [events](./events/) folder in this project. SAM provides the capability of generating additional synthetic events for a variety of AWS services. [Read the documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-local-generate-event.html).

Use the following command to learn more about generating synthetic events:
```bash
# generate a synthetic event
typescript-test-intro$ sam local generate-event
```
[[top]](#typescript-test-intro)

## Working with local emulators

Local emulation of AWS services offers a simple way to build and test cloud native applications using local resources. Local emulation can speed up the build and deploy cycle creating faster feedback loops for application developers. 

Local emulation has several limitations. Cloud services evolve rapidly, so local emulators are unlikely to have feature parity with their counterpart services in the cloud. Local emulators may not be able to provide an accurate representation of IAM permissions or service quotas. Local emulators do not exist for every AWS service.

SAM provides local emulation features for [AWS Lambda](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-invoke.html) and [Amazon API Gateway](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-start-api.html). AWS provides [Amazon DynamoDB Local](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html) as well as [AWS Step Functions Local](https://docs.aws.amazon.com/step-functions/latest/dg/sfn-local.html). Third party vendors like [LocalStack](https://docs.localstack.cloud/overview/) may provide emulation for additional AWS services. 

[[top]](#typescript-test-intro)

## Run a unit test using a mock framework

Lambda functions frequently call other AWS or 3rd party services. Mock frameworks are useful to simulate service responses. Mock frameworks can speed the development process by enabling rapid feedback iterations. Mocks can be particularly useful for testing failure cases when testing these branches of logic are difficult to do in the cloud.

This project [uses mocks](./list-buckets/tests/unit/list-buckets.test.ts#L39) to test the internal logic of a Lambda function. 
The project uses the [aws-sdk-client-mock](https://m-radzikowski.github.io/aws-sdk-client-mock/) dependency library to mock an external service call to Amazon S3. The `aws-sdk-client-mock` library can simulate responses from [AWS services](https://m-radzikowski.github.io/aws-sdk-client-mock/#mock), or for specific client instances. Tests with mocks are defined in the `tests/unit` folder. Use `npm` to install test dependencies and `jest` to run the unit test.

```bash
# move to lambda-specific directory
typescript-test-intro$ cd list-buckets

# install dev dependencies
list-buckets$ npm install

# run unit tests with mocks
list-buckets$ npm test unit
```

[[top]](#typescript-test-intro)

## Run integration tests against cloud resources

[Integration tests](./list-buckets/tests/integration/api.test.ts) run against deployed cloud resources. Since local unit tests cannot adequately test IAM permissions or other policy configurations, our integration tests confirm that permissions are properly configured. Run integration tests against your deployed cloud resources with the following command:

```bash
# move to lambda-specific directory
typescript-test-intro$ cd list-buckets

# Set the environment variable API_URL to the base of the ListBucketsApi CloudFormation output from the deploy step above
# E.g. https://aaaaaaaaaaa.execute-api.us-east-2.amazonaws.com/Prod
# You can do this as a separate step if you prefer
list-buckets$ API_URL=https://YOUR_API_URL npm test integration
```

[[top]](#typescript-test-intro)

## Invoke a Lambda function in the cloud

The `AWS CLI` enables you to invoke a Lambda function in the cloud.

```bash
# invoke a Lambda function in the cloud using the AWS CLI
# replace YOUR_LAMBDA_NAME with the full name of your lambda
# you can find this in the ListBucketsFunction output of the deploy step above
# E.g. typescript-test-intro-ListBucketsFunction-aaaaaaaaaaaaa
aws lambda invoke --function-name YOUR_FULL_LAMBDA_NAME outfile.txt
```

[[top]](#typescript-test-intro)

## Fetch, tail, and filter Lambda function logs

To simplify troubleshooting, SAM CLI has a command called `sam logs`. `sam logs` lets you fetch logs generated by your deployed Lambda function from the command line. In addition to printing the logs on the terminal, this command has several nifty features to help you quickly find the bug.

`NOTE`: This command works for all AWS Lambda functions; not just the ones you deploy using SAM.

```bash
typescript-test-intro$ sam logs -n ListBucketsFunction --stack-name typescript-test-intro --tail
```

You can find more information and examples about filtering Lambda function logs in the [SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-logging.html).

[[top]](#typescript-test-intro)

## Use SAM Accerate to speed up feedback cycles

AWS SAM Accelerate is a set of features that reduces deployment latency and enable developers to test their code quickly against production AWS services in the cloud.
[Read the blog post](https://aws.amazon.com/blogs/compute/accelerating-serverless-development-with-aws-sam-accelerate/)

```bash
# synchronize local code with the cloud
typescript-test-intro$ sam sync --watch --stack-name typescript-test-intro
```

AWS Cloud Development Kit (CDK) has a similar synchronization feature, `cdk watch`. To learn more about `cdk watch` read this [blog post](https://aws.amazon.com/blogs/developer/increasing-development-speed-with-cdk-watch/). 

[[top]](#typescript-test-intro)

## Implement application tracing
You can use AWS X-Ray to track user requests as they travel through your entire application. With X-Ray, you can understand how your application and its underlying services are performing to identify and troubleshoot the root cause of performance issues and errors.

This [Lambda function](./list-buckets/app.ts) handler has been instrumented using AWS X-Ray. Find to your Lambda function in the console. Then navigate to `Monitor` -> `Traces` and you should see a graph of your X-Ray trace.

You may also navigate to the [X-Ray service](https://console.aws.amazon.com/xray/home) in the console to examine your traces in greater detail.

[[top]](#typescript-test-intro)

## Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
aws cloudformation delete-stack --stack-name typescript-test-intro
```

## Additional Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

Next, you can use AWS Serverless Application Repository to deploy ready to use Apps that go beyond hello world samples and learn how authors developed their applications: [AWS Serverless Application Repository main page](https://aws.amazon.com/serverless/serverlessrepo/)
