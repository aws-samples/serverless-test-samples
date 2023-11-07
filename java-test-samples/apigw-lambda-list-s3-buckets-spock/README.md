# Java Test Samples Starter Project
This project contains automated test code samples for serverless applications. The project uses the [AWS Serverless Application Model](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) (SAM) CLI for configuration, testing and deployment.

- [Project contents](#project-contents)
- [Prerequisites](#prerequisites)
- [Build and deploy with the SAM CLI](#build-and-deploy-with-the-sam-cli)
- [Working with events](#working-with-events)
- [Working with local emulators](#working-with-local-emulators)
    - [Use the SAM Lambda emulator](#use-the-sam-lambda-emulator)
    - [Use the SAM API Gateway emulator](#use-the-sam-api-gateway-emulator)
- [Run a unit test using a mock framework](#run-a-unit-test-using-a-mock-framework)
- [Run an integration test against cloud resources](#run-integration-tests-against-cloud-resources)
- [Invoke a Lambda function in the cloud](#invoke-a-lambda-function-in-the-cloud)
- [Fetch, tail, and filter Lambda function logs locally](#fetch-tail-and-filter-lambda-function-logs-locally)
- [Use SAM Accelerate to speed up feedback cycles](#use-sam-accelerate-to-speed-up-feedback-cycles)
- [Perform a load test](#perform-a-load-test)
- [Cleanup](#cleanup)
- [Additional resources](#additional-resources)

## Project contents
This application creates several AWS resources, including a Lambda function and an API Gateway. These resources are defined in the `template.yaml` file in this project. This project includes the following files and folders:

- src - Code for the application's Lambda function.
- events - synthetic events that you can use to invoke the function.
- tests - Unit and integration tests for the application code.
- template.yaml - A template that defines the application's AWS resources.

[[top]](#api-gateway-to-lambda-to-list-s3-buckets)

## Prerequisites
The Serverless Application Model Command Line Interface (SAM CLI) is an extension of the AWS CLI that adds functionality for building and testing Lambda applications. It uses Docker to run your functions in an Amazon Linux environment that matches Lambda. It can also emulate your application's build environment and API.

To use the SAM CLI, you need the following tools.

* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* Java11 - [Install the Java 11](https://docs.aws.amazon.com/corretto/latest/corretto-11-ug/downloads-list.html)
* Maven - [Install Maven](https://maven.apache.org/install.html)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

[[top]](#api-gateway-to-lambda-to-list-s3-buckets)

## Build and deploy with the SAM CLI
Use the following command to build your application locally:

```bash
# build your application locally using a sam
apigw-lambda-list-s3-buckets$ sam build
```
The SAM CLI installs dependencies defined in `apigw-lambda-list-s3-buckets/pom.xml`, creates a deployment package, and saves it in the `.aws-sam/build` folder. [Read the documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-building.html).

> Note:
> If you witness error `Could not find public.ecr.aws/sam/build-java11:latest-x86_64 image locally and failed to pull it from docker` then run `docker logout public.ecr.aws` and rerun `sam build`

Use the following commend to deploy your application package to AWS:
``` bash
# deploy your application to the AWS cloud 
apigw-lambda-list-s3-buckets$ sam deploy --guided
```
After running this command you will receive a series of prompts:

* **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, and a good starting point would be something matching your project name.
* **AWS Region**: The AWS region you want to deploy your app to.
* **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review. If set to no, the AWS SAM CLI will automatically deploy application changes.
* **Allow SAM CLI IAM role creation**: Many AWS SAM templates, including this example, create AWS IAM roles required for the AWS Lambda function(s) included to access AWS services. By default, these are scoped down to minimum required permissions. To deploy an AWS CloudFormation stack which creates or modifies IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be provided. If permission isn't provided through this prompt, to deploy this example you must explicitly pass `--capabilities CAPABILITY_IAM` to the `sam deploy` command.
* **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.

You can find your API Gateway Endpoint URL in the output values displayed after deployment.
Take note of this URL for use in the logging section below. On subsequent deploys you can run `sam deploy` without the `--guided` flag. [Read the documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-deploying.html).

[[top]](#api-gateway-to-lambda-to-list-s3-buckets)

## Working with events
Testing event driven architectures often requires working with synthetic events. Events are frequently defined as JSON documents. Synthetic events are test data that represent AWS events such as a requests from API Gateway or a messages from SQS.

AWS Lambda always requires an event during invocation. A sample test event is included in the `events` folder in this project. SAM provides the capability of generating additional synthetic events for a variety of AWS services. [Read the documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-local-generate-event.html).

Use the following command to learn more about generating synthetic events:
```bash
# generate a synthetic event
apigw-lambda-list-s3-buckets$ sam local generate-event
```

[[top]](#api-gateway-to-lambda-to-list-s3-buckets)

## Use the SAM Lambda emulator
The SAM CLI can emulate a Lambda function inside a Docker container deployed to your local desktop. To use this feature, invoke the function with the `sam local invoke` command passing a synthetic event. Print statements log to standard out. [Read the documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-invoke.html).

```bash
# invoke a Lambda function locally
apigw-lambda-list-s3-buckets$ sam local invoke ListBucketsFunction --event events/event.json
```

The `sam local start-lambda` command starts a local endpoint that emulates the AWS Lambda invoke endpoint. You can invoke it from your automated tests. Because this endpoint emulates the AWS Lambda invoke endpoint, you can write tests and then run them against the local Lambda emulator. You can also run the same tests against a deployed AWS SAM stack in your CI/CD pipeline. [Read the documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-automated-tests.html).

```bash
# start a local emulator for a Lambda function endpoint
apigw-lambda-list-s3-buckets$ sam local start-lambda --region us-east-1
```

```bash
# run a unit test in a separate terminal
apigw-lambda-list-s3-buckets$ aws lambda invoke --function-name "ListBucketsFunction" --endpoint-url "http://127.0.0.1:3001" --no-verify-ssl out.txt
```

[[top]](#api-gateway-to-lambda-to-list-s3-buckets)

## Use the SAM API Gateway emulator
The SAM CLI can also emulate your application's API. Use the `sam local start-api` to run the API locally on port 3000.

```bash
# start a local emulator for an API Gateway endpoint
apigw-lambda-list-s3-buckets$ sam local start-api
```

```bash
# make a request to the endpoint in a separate terminal
apigw-lambda-list-s3-buckets$ curl http://localhost:3000/listBuckets
```

The SAM CLI reads the application template to determine the API's routes and the functions that they invoke. The `Events` property on each function's definition includes the route and method for each path.

```yaml
Events:
HelloWorld:
  Type: Api
  Properties:
    Path: /listBuckets
    Method: get
```

[[top]](#api-gateway-to-lambda-to-list-s3-buckets)

## Run unit tests

Tests are defined in the `apigw-lambda-list-s3-buckets/src/test` folder in this project.

```bash
apigw-lambda-list-s3-buckets$ mvn test
```

[[top]](#api-gateway-to-lambda-to-list-s3-buckets)

## Run a unit test using a mock framework
You can use Spock to mock the service calls that are being done in the Lambda function.
[`AppWithMockSpec.groovy`](./src/test/groovy/com/example/AppWithMockSpec.groovy) covers this example:

```groovy
class AppWithMockSpec  extends Specification {


    def mockS3Client = Mock(S3Client)
    def app = new App(mockS3Client)

    def "returns a list of buckets"() {
        given: "a bucket exists"
        1 * mockS3Client.listBuckets() >> listWithBucket()

        when: "a request is received"
        def request =  getRequestFromFile()
        def responseEvent = app.handleRequest(request, null)

        then: "a list of buckets is returned"
        def responseBody = new JsonSlurper().parseText(responseEvent.getBody()) as List
        responseBody.size() >= 1

        and: "the first item is the example bucket"
        responseBody.first() == TEST_BUCKET_NAME
    }
}
```

[[top]](#api-gateway-to-lambda-to-list-s3-buckets)

## Invoke a Lambda function in the cloud
The `AWS CLI` enables you to invoke a Lambda function in the cloud.

```bash
# invoke a Lambda function in the cloud using the AWS CLI
aws lambda invoke --function-name <function-name> outfile.txt
```

[[top]](#api-gateway-to-lambda-to-list-s3-buckets)

## Fetch, tail, and filter Lambda function logs locally
To simplify troubleshooting, SAM CLI has a command called `sam logs`. The `sam logs` command lets you fetch logs generated by your deployed Lambda function from the command line. In addition to printing the logs on the terminal, this command has several features to help you quickly find your bug.

`NOTE`: This command works for all AWS Lambda functions; not just the ones you deploy using SAM.

```bash
apigw-lambda-list-s3-buckets$ sam logs -n ListBucketsFunction --stack-name <stack-name> --tail
```

In a new terminal, curl the API Gateway and watch the log output.

```bash
apigw-lambda-list-s3-buckets$ curl <API Gateway url>
```

You can find more information and examples about filtering Lambda function logs in the [SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-logging.html).

[[top]](#api-gateway-to-lambda-to-list-s3-buckets)

## Use SAM Accelerate to speed up feedback cycles
AWS SAM Accelerate is a set of features that reduces deployment latency and enable developers to test their code quickly against production AWS services in the cloud.
[Read the blog post](https://aws.amazon.com/blogs/compute/accelerating-serverless-development-with-aws-sam-accelerate/)

```bash
# synchronize local code with the cloud
apigw-lambda-list-s3-buckets$ sam sync --watch --stack-name <stack-name>
```

[[top]](#api-gateway-to-lambda-to-list-s3-buckets)

## Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
apigw-lambda-list-s3-buckets$ sam delete
```

## Additional Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

Next, you can use AWS Serverless Application Repository to deploy ready to use Apps that go beyond hello world samples and learn how authors developed their applications: [AWS Serverless Application Repository main page](https://aws.amazon.com/serverless/serverlessrepo/)


[[top]](#api-gateway-to-lambda-to-list-s3-buckets)

## Working with local emulators
Local emulation of AWS services offers a simple way to build and test cloud native applications using local resources. Local emulation can speed up the build and deploy cycle creating faster feedback loops for application developers.

Local emulation has several limitations. Cloud services evolve rapidly, so local emulators are unlikely to have feature parity with their counterpart services in the cloud. Local emulators may not be able to provide an accurate representation of IAM permissions or service quotas. Local emulators do not exist for every AWS service.

SAM provides local emulation features for [AWS Lambda](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-invoke.html) and [Amazon API Gateway](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-start-api.html). AWS provides [Amazon DynamoDB Local](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html) as well as [AWS Step Functions Local](https://docs.aws.amazon.com/step-functions/latest/dg/sfn-local.html).

This project demonstrates local emulation of Lambda and API Gateway with SAM.

[[top]](#api-gateway-to-lambda-to-list-s3-buckets)
