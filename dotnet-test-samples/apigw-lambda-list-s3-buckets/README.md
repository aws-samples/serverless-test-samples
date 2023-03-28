# .NET Test Samples Starter Project

This project contains automated test sample code samples for serverless applications. The project uses the [AWS Serverless Application Model](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) (SAM) CLI for configuration, testing and deployment. 

- [Project contents](#project-contents)
- [Prerequisites](#prerequisites)
- [Build and deploy with the SAM CLI](#build-and-deploy-with-the-sam-cli)
- [Working with events](#working-with-events)
- [Run a unit test using a mock framework](#run-a-unit-test-using-a-mock-framework)
- [Run an integration test against cloud resources](#run-integration-tests-against-cloud-resources)
- [Invoke a Lambda function in the cloud](#invoke-a-lambda-function-in-the-cloud)
- [Fetch, tail, and filter Lambda function logs locally](#fetch-tail-and-filter-lambda-function-logs-locally)
- [Use SAM Accerate to speed up feedback cycles](#use-sam-accerate-to-speed-up-feedback-cycles)
- [Use CDK Watch to speed up feedback cycles](#use-cdk-watch-to-speed-up-feedback-cycles)
- [Working with local emulators](#working-with-local-emulators)
  - [Use the SAM Lambda emulator](#use-the-sam-lambda-emulator)
  - [Use the SAM API Gateway emulator](#use-the-sam-api-gateway-emulator)
- [Implement application tracing](#implement-application-tracing)
- [Cleanup](#cleanup)
- [Additional resources](#additional-resources)

## Project contents
This application creates several AWS resources, including a Lambda function and an API Gateway. These resources are defined in the `template.yaml` file in this project. This project includes the following files and folders:

- src - Code for the application's Lambda function.
- events - synthetic events that you can use to invoke the function.
- tests - Unit and integration tests for the application code. 
- template.yaml - A template that defines the application's AWS resources.

## Prerequisites
The SAM CLI is an extension of the AWS CLI that adds functionality for building and testing serverless applications. It contains features for building your application locally, deploying it to AWS, and emulating AWS services locally to support automated unit tests.  

To use the SAM CLI, you need the following tools.

* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* .NET 6 - [Install .NET 6](https://dotnet.microsoft.com/en-us/download/dotnet/6.0)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

[[top]](#dotnet-test-samples)

## Build and deploy with the SAM CLI
Use the following command to build your application locally: 

```bash
# build your application locally using a container
dotnet-test-samples$ sam build
```
The SAM CLI installs runs a dotnet publish for each function defined in the template, creates a deployment package, and saves it in the `.aws-sam/build` folder. [Read the documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-building.html).

Use the following command to deploy your application package to AWS: 

``` bash
# deploy your application to the AWS cloud 
dotnet-test-samples$ sam deploy --guided
```

After running this command you will receive a series of prompts:

* **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, and a good starting point would be something matching your project name. Use `dotnet-intro-test-samples` as the stack name for this project.
* **AWS Region**: The AWS region you want to deploy your app to, the test projects are configured to default to us-east-1.
* **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review. If set to no, the AWS SAM CLI will automatically deploy application changes.
* **Allow SAM CLI IAM role creation**: Many AWS SAM templates, including this example, create AWS IAM roles required for the AWS Lambda function(s) included to access AWS services. By default, these are scoped down to minimum required permissions. To deploy an AWS CloudFormation stack which creates or modifies IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be provided. If permission isn't provided through this prompt, to deploy this example you must explicitly pass `--capabilities CAPABILITY_IAM` to the `sam deploy` command.
* **DotnetTestDemo may not have authorisation defined, Is this okay?**: If a Lambda function is defined with an API event that does not have authorisation defined the AWS SAM CLI will ask you to confirm that this is ok.
* **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.

You can find your API Gateway Endpoint URL in the output values displayed after deployment. Take note of this URL for use in the logging section below. On subsequent deploys you can run `sam deploy` without the `--guided` flag. [Read the documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-deploying.html).
[top](#dotnet-test-samples)

## Working with events
Testing event driven architectures often requires working with synthetic events. Events are frequently defined as JSON documents. Synthetic events are test data that represent AWS events such as a requests from API Gateway or a messages from SQS. 

AWS Lambda always requires an event during invocation. A sample test event is included in the `events` folder in this project. SAM provides the capability of generating additional synthetic events for a variety of AWS services. [Read the documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-local-generate-event.html).

Use the following command to learn more about generating synthetic events:
```bash
# generate a synthetic event
dotnet-test-samples$ sam local generate-event
```
[[top]](#dotnet-test-samples)

## Project Structure

The project splits out the Lambda function, core business logic and integrations into separate libraries. This allows for a clear separation of concerns between parts of the application and keeps it maintainable, portable and testable.

### ServerlessTestSamples.Core

This library contains the business logic with *no external dependencies*. All integrations are abstracted away behind clearly defined interfaces. For example, the interaction with the storage layer uses an `IStorageService` interface:

```c#
namespace ServerlessTestSamples.Core.Services;

public interface IStorageService
{
    Task<ListStorageAreasResult> ListStorageAreas(string? filterPrefix, CancellationToken cancellationToken);
}
```

The business logic to query the available storage areas has no external dependencies and can be tested completely independently.

```c#
public class ListStorageAreasQueryHandler
{
    private readonly IStorageService _storageService;
    private readonly ILogger<ListStorageAreasQueryHandler> _logger;
    
    public ListStorageAreasQueryHandler(
        IStorageService storageService,
        ILogger<ListStorageAreasQueryHandler> logger)
    {
        _storageService = storageService;
        _logger = logger;
    }

    public async Task<ListStorageAreasQueryResult> Handle(
        ListStorageAreasQuery query,
        CancellationToken cancellationToken)
    {
        ListStorageAreasResult result;

        try
        {
            result = await _storageService.ListStorageAreas(query.FilterPrefix, cancellationToken);
        }
        catch (Exception ex)
        {
            this._logger.LogError(ex, "Failure querying storage areas");
            
            return new ListStorageAreasQueryResult(new List<string>(capacity: 0));
        }

        if (!result.IsSuccess)
        {
            this._logger.LogWarning(result.Message);
        }

        return new ListStorageAreasQueryResult(result.StorageAreas);
    }
}
```

### ServerlessTestSamples.Integrations

This project contains all code that handles integrations your application has. This includes databases, caches, 3rd party API's. All implementation logic is stored in this one library.

In this case, the implementation of our storage service to interact with Amazon S3 is included here

```c#
public class S3StorageService : IStorageService
{
    private readonly IAmazonS3 _client;

    public S3StorageService(IAmazonS3 client) => _client = client;

    public async Task<ListStorageAreasResult> ListStorageAreas(
        string? filterPrefix,
        CancellationToken cancellationToken)
    {
        var buckets = await _client.ListBucketsAsync(cancellationToken);

        if (buckets.HttpStatusCode != HttpStatusCode.OK)
        {
            return new(Enumerable.Empty<string>(), false, "Failure retrieving services from Amazon S3");
        }

        return new(buckets.Buckets.Select(p => p.BucketName));
    }
}
```

### Lambda Functions

Outside of these two shared libraries, there is then a separate project per Lambda function. This provides a clear separation of concerns and ensures the functions have a single purpose.

The way we initialize our Lambda function is important for testing. The Lambda service always requires a parameterless constructor for initialization. However, all our function initialization logic is included in an internal constructor. This allows mock implementations to be used for testing.    

```c#
public class Function
{
    private readonly ListStorageAreasQueryHandler _queryHandler;
    private readonly ILogger<Function> _logger;
    private readonly IOptions<JsonSerializerOptions> _jsonOptions;

    public Function() : this(Startup.ServiceProvider) { }

    public Function(
        ListStorageAreasQueryHandler handler,
        ILogger<Function> logger,
        IOptions<JsonSerializerOptions> jsonOptions)
        : this(NewServiceProvider(handler, logger, jsonOptions)) { }

    private Function(IServiceProvider serviceProvider)
    {
        _queryHandler = serviceProvider.GetRequiredService<ListStorageAreasQueryHandler>();
        _logger = serviceProvider.GetRequiredService<ILogger<Function>>();
        _jsonOptions = serviceProvider.GetRequiredService<IOptions<JsonSerializerOptions>>();
        AWSSDKHandler.RegisterXRayForAllServices();
    }

    private static IServiceProvider NewServiceProvider(
        ListStorageAreasQueryHandler handler,
        ILogger<Function> logger,
        IOptions<JsonSerializerOptions> jsonOptions)
    {
        var container = new System.ComponentModel.Design.ServiceContainer();

        container.AddService(typeof(ListStorageAreasQueryHandler), handler);
        container.AddService(typeof(ILogger<Function>), logger);
        container.AddService(typeof(IOptions<JsonSerializerOptions>), jsonOptions);

        return container;
    }
    ...
}
```

[[top]](#dotnet-test-samples)

## Run a unit test using a mock framework
Lambda functions frequently call other AWS or 3rd party services. Mock frameworks are useful to simulate service responses. Mock frameworks can speed the development process by enabling rapid feedback iterations. Mocks can be particularly useful for testing failure cases when testing these branches of logic are difficult to do in the cloud.

This project demonstrates how to run tests on both our core business logic, and also for unit testing our Lambda function code itself.

The project uses [xUnit](https://xunit.net/) as the test framework and [Moq](https://github.com/moq/moq4) to provide mocking.

### Testing Business Logic

Business logic tests can be found in the [MockBusinessLogicTests.cs](./tests/ServerlessTestSamples.UnitTest/MockBusinessLogicTests.cs) file.

```c#
[Fact]
public async Task TestCoreBusinessLogicWithSuccessfulResponse_ShouldReturnStorageAreas()
{
    var mockStorageService = new Mock<IStorageService>();
    
    mockStorageService.Setup(s => s.ListStorageAreas(It.IsAny<string>(), It.IsAny<CancellationToken>()))
                      .ReturnsAsync(new List<string>()
                       {
                           "bucket1",
                           "bucket2",
                           "bucket3",
                       });
    
    var queryHandler = new ListStorageAreasQueryHandler(mockStorageService.Object);
    var queryResult = await queryHandler.Handle(new ListStorageAreasQuery()
    {
        FilterPrefix = string.Empty,
    });

    queryResult.Should().BeEquivalentTo(
        new ListStorageAreasQueryResult(
            new[]
            {
                "bucket1",
                "bucket2",
                "bucket3",
            }));
}
```

Using Moq, it is possible to create a Mock implementation of any object. Once mocked, it is possible to setup how different methods will be invoked.

In this example, a mock implementation of the ListStorageAreas is added that will be invoked. The It.IsAny<string>() line determines which parameters will cause this mock to be invoked. In this case, if any string is passed into the method this mock will be invoked. The ReturnsAsync method then allows us to define what will be be returned by the mock. In this instance, we are returning a hardcoded list of strings.

When the ListStorageAreasQueryHandler is initialised the instance of our mock storage service is passed in.

### Mocking integrations

Another strategy for mocking is to mock the integrations with 3rd parties. An example of this would be to move the AWS SDK calls. An example of this can be seen in [MockSdkTests.cs](./tests/ServerlessTestSamples.UnitTest/MockSdkTests.cs).

In the below code sample we are testing our function logic and that the ApiGateway response is what is expected. A mock implementation of the AmazonS3Client is created and the ListBucketsAsync method is mocked.

This is a useful approach, but can be brittle as the AWS API's change regularly. There is no guarantee that your mocked response will match how response from the actual API call. This is a great reason to test in the cloud as quickly as possible.

```c#
[Fact]
public async Task TestLambdaHandlerWithValidS3Response_ShouldReturnSuccess()
{
    var mockedS3Client = new Mock<IAmazonS3>();
    
    mockedS3Client.Setup(p => p.ListBucketsAsync(It.IsAny<CancellationToken>()))
                  .ReturnsAsync(new ListBucketsResponse()
                   {
                       Buckets = new List<S3Bucket>()
                       {
                           new S3Bucket(){ BucketName = "bucket1" },
                           new S3Bucket(){ BucketName = "bucket2" },
                           new S3Bucket(){ BucketName = "bucket3" },
                       },
                       HttpStatusCode = HttpStatusCode.OK,
                   });
    
    var storageService = new S3StorageService(mockedS3Client.Object);
    var jsonOptions = Options.Create(new JsonSerializerOptions(JsonSerializerDefaults.Web));
    var handler = new ListStorageAreasQueryHandler(
        storageService,
        Mock.Of<ILogger<ListStorageAreasQueryHandler>());
    var function = new Function(handler, Mock.Of<ILogger<Function>(), jsonOptions);

    var result = await function.Handler(new APIGatewayProxyRequest(), new TestLambdaContext());

    result.StatusCode.Should().Be(200);

    var body = JsonSerializer.Deserialize<ListStorageAreaResponseBody>(result.Body, jsonOptions.Value);

    body.Should().BeEquivalentTo(
            new ListStorageAreaResponseBody()
            {
                StorageAreas = new[]
                {
                    "bucket1",
                    "bucket2",
                    "bucket3",
                },
            });
}
```

Another useful feature of Moq is the ability to test exceptions. In the below example, instead of mocking the response of the method call an Exception is thrown. This allows a test to be written to understand what would happen if the S3 SDK threw an exception.  

```c#
[Fact]
public async Task TestLambdaHandlerWithS3Exception_ShouldReturnEmpty()
{
    var mockedS3Client = new Mock<IAmazonS3>();
    
    mockedS3Client.Setup(p => p.ListBucketsAsync(It.IsAny<CancellationToken>()))
                  .ThrowsAsync(new AmazonS3Exception("Mock S3 failure"));
    
    var storageService = new S3StorageService(mockedS3Client.Object);
    var jsonOptions = Options.Create(new JsonSerializerOptions(JsonSerializerDefaults.Web));
    var handler = new ListStorageAreasQueryHandler(
        storageService,
        Mock.Of<ILogger<ListStorageAreasQueryHandler>());
    var function = new Function(handler, Mock.Of<ILogger<Function>(), jsonOptions);

    var result = await function.Handler(new APIGatewayProxyRequest(), new TestLambdaContext());

    result.StatusCode.Should().Be(200);

    var body = JsonSerializer.Deserialize<ListStorageAreaResponseBody>(result.Body, jsonOptions.Value);

    body.Should().BeEquivalentTo(new ListStorageAreaResponseBody());
}
```

To execute the tests, run the below commands from a terminal.

```bash

# run unit tests with mocks
dotnet-test-samples$ dotnet test .\tests\ServerlessTestSamples.UnitTest\
```

[[top]](#dotnet-test-samples)

## Run integration tests against cloud resources
Integration tests run against deployed cloud resources. Since local unit tests cannot adequately test IAM permissions, our integration tests confirm that permissions are properly configured. Run integration tests against your deployed cloud resources with the following command:

```bash
# Set the environment variable AWS_SAM_STACK_NAME to the name of the stack you specified during deploy
dotnet-test-samples$ AWS_SAM_STACK_NAME=<stack-name> dotnet test .\tests\ServerlessTestSamples.IntegrationTest\
```

The sample integration test is straightforward. The [Setup.cs](./tests/ServerlessTestSamples.IntegrationTest/Setup.cs) is performed using the [class fixture feature of xUnit.](https://xunit.net/docs/shared-context) Class fixtures allow code to be executed once and then shared between all unit tests in a class. In this example, we use the class fixture to retrieve the API URL and store it for future reference. This class fixture could be used to create any hardcoded resources to use for testing. The `Setup` class also implements `IAsyncLifetime`, meaning that any test initialization or cleanup can be executed asynchronously.

```c#
public async Task InitializeAsync()
{
    var stackName = System.Environment.GetEnvironmentVariable("AWS_SAM_STACK_NAME") ?? "dotnet-test-samples";
    var region = System.Environment.GetEnvironmentVariable("AWS_SAM_REGION_NAME") ?? "us-east-1";
    var cloudFormationClient = new AmazonCloudFormationClient(new AmazonCloudFormationConfig()
    {
        RegionEndpoint = RegionEndpoint.USEast1,
    });
    var response = await cloudFormationClient.DescribeStacksAsync(new DescribeStacksRequest()
    {
        StackName = stackName
    });
    var output = response.Stacks[0].Outputs.FirstOrDefault(p => p.OutputKey == "ApiEndpoint");

    ApiUrl = output.OutputValue;
}
```

Once the API Url has been set, we can then use that in an integration test to ensure the code works as expected.

```c#
public IntegrationTest(Setup setup)
{
    _httpClient = new HttpClient()
    {
        BaseAddress = new Uri(setup.ApiUrl),
        DefaultRequestHeaders =
        {
            { "INTEGRATION_TEST", "true" },
        },
    };
}

[Fact]
public async Task ListStorageAreas_ShouldReturnSuccess()
{
    var result = await _httpClient.GetAsync("storage");

    result.StatusCode.Should().Be(HttpStatusCode.OK);

    var storageAreasResult = await response.Content.ReadFromJsonAsync<ListStorageAreasResult>();

    storageAreasResult.StorageAreas.Should().NotBeNull();
    storageAreasResult.IsSuccess.Should().BeTrue();
}
```

[[top]](#dotnet-test-samples)

## Directly invoke a Lambda function in the cloud
The `AWS CLI` enables you to invoke a Lambda function in the cloud.

```bash
# invoke a Lambda function in the cloud using the AWS CLI
aws lambda invoke --function-name dotnet-test-samples-DotnetTestDemo-hqVByFXNxqBC outfile.txt
```
[[top]](#dotnet-test-samples)

## Fetch, tail, and filter Lambda function logs locally
To simplify troubleshooting, SAM CLI has a command called `sam logs`. The `sam logs` command lets you fetch logs generated by your deployed Lambda function from the command line. In addition to printing the logs on the terminal, this command has several features to help you quickly find your bug.

`NOTE`: This command works for all AWS Lambda functions; not just the ones you deploy using SAM.

```bash
dotnet-test-samples$ sam logs -n DotnetTestDemo --stack-name dotnet-test-samples --tail
```

In a new terminal, curl the API Gateway and watch the log output.

```bash
dotnet-test-samples$ curl <API Gateway url>
```

You can find more information and examples about filtering Lambda function logs in the [SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-logging.html).

[[top]](#dotnet-test-samples)

## Use SAM Accerate to speed up feedback cycles
AWS SAM Accelerate is a set of features that reduces deployment latency and enable developers to test their code quickly against production AWS services in the cloud.
[Read the blog post](https://aws.amazon.com/blogs/compute/accelerating-serverless-development-with-aws-sam-accelerate/)

```bash
# synchronize local code with the cloud
dotnet-test-samples$ sam sync --watch --stack-name dotnet-test-samples
```

[[top]](#dotnet-test-samples)
## Working with local emulators
Local emulation of AWS services offers a simple way to build and test cloud native applications using local resources. Local emulation can speed up the build and deploy cycle creating faster feedback loops for application developers.

Local emulation has several limitations. Cloud services evolve rapidly, so local emulators are unlikely to have feature parity with their counterpart services in the cloud. Local emulators may not be able to provide an accurate representation of IAM permissions or service quotas. Local emulators do not exist for every AWS service.

SAM provides local emulation features for [AWS Lambda](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-invoke.html) and [Amazon API Gateway](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-start-api.html). AWS provides [Amazon DynamoDB Local](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html) as well as [AWS Step Functions Local](https://docs.aws.amazon.com/step-functions/latest/dg/sfn-local.html). Third party vendors like [LocalStack](https://docs.localstack.cloud/overview/) may provide emulation for additional AWS services.

This project demonstrates local emulation of Lambda and API Gateway with SAM.

[[top]](#dotnet-test-samples)

## Use the SAM Lambda emulator
The SAM CLI can emulate a Lambda function inside a Docker container deployed to your local desktop. To use this feature, invoke the function with the `sam local invoke` command passing a synthetic event. Print statements log to standard out. [Read the documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-invoke.html).

[[top]](#dotnet-test-samples)

## Use the SAM API Gateway emulator

The SAM CLI reads the application template to determine the API's routes and the functions that they invoke. The `Events` property on each function's definition includes the route and method for each path.

```yaml
      Events:
        HelloWorld:
          Type: Api
          Properties:
            Path: /hello
            Method: get
```
[[top]](#dotnet-test-samples)

## Implement application tracing
You can use AWS X-Ray to track user requests as they travel through your entire application. With X-Ray, you can understand how your application and its underlying services are performing to identify and troubleshoot the root cause of performance issues and errors.

X-Ray tracing is configured in .NET using the AWSXRayRecorder libraries. Automatic instruementation can be added for:

- AWSSDK calls
- External HTTP requests
- SQL queries

To enable this for AWS Lambda the SAM template and function code both need to be updated.

### SAM Template

Tracing needs to be enabled in the SAM template for both the API and Lambda function. Enable this with the two additional tracing properties in the Globals section of the SAM template.

``` yaml
Globals:
  Function:
#    Tracing: PassThrough
    Timeout: 10
    Runtime: dotnet6
    Architectures:
      - arm64
#  Api:
#    TracingEnabled: True
```

### Function Code

Instrumentation then needs to be added in the Function code. In this example tracing is enabled for all AWS SDK calls. There are [various auto-instrumentation libraries available including HTTP and SQL.](https://docs.aws.amazon.com/xray/latest/devguide/xray-sdk-dotnet.html)

```c#
internal Function(ListStorageAreasQueryHandler handler, ILogger<Function> logger)
{
    AWSSDKHandler.RegisterXRayForAllServices();
            
    _queryHandler = handler ?? Startup.ServiceProvider.GetRequiredService<ListStorageAreasQueryHandler>();
    _logger = logger ?? Startup.ServiceProvider.GetRequiredService<ILogger<Function>>();
}
```

Further details on instrumenting with the [AWS XRay Recorder library are found in the AWS Docs.](https://docs.aws.amazon.com/xray/latest/devguide/xray-sdk-dotnet-segment.html) 

[[top]](#dotnet-test-samples)

## Cleanup

To delete the sample application that you created, use the SAM CLI.

```bash
sam delete
```

## Additional Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

Next, you can use AWS Serverless Application Repository to deploy ready to use Apps that go beyond hello world samples and learn how authors developed their applications: [AWS Serverless Application Repository main page](https://aws.amazon.com/serverless/serverlessrepo/)
