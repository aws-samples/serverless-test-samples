# .NET Test Samples API Tests

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

* **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, and a good starting point would be something matching your project name. Use `dotnet-api-test-samples` as the stack name for this project.
* **AWS Region**: The AWS region you want to deploy your app to, the test projects are configured to default to `us-east-1`.
* **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review. If set to no, the AWS SAM CLI will automatically deploy application changes.
* **Allow SAM CLI IAM role creation**: Many AWS SAM templates, including this example, create AWS IAM roles required for the AWS Lambda function(s) included to access AWS services. By default, these are scoped down to minimum required permissions. To deploy an AWS CloudFormation stack which creates or modifies IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be provided. If permission isn't provided through this prompt, to deploy this example you must explicitly pass `--capabilities CAPABILITY_IAM` to the `sam deploy` command.
* **DotnetTestDemo may not have authorisation defined, Is this okay?**: If a Lambda function is defined with an API event that does not have authorisation defined the AWS SAM CLI will ask you to confirm that this is ok.
* **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.

You can find your API Gateway Endpoint URL in the output values displayed after deployment. Take note of this URL for use in the logging section below. On subsequent deploys you can run `sam deploy` without the `--guided` flag. [Read the documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-deploying.html).
[top](#dotnet-test-samples)

## Project Structure

The project splits out the Lambda function, core business logic and integrations into seperate libraries. This allows for a clear seperation of concerns between parts of the application and keeps it maintainable, portable and testable.

### ServerlessTestApi.Core

This library contains the business logic with *no external dependencies*. All integrations are abstracted away behind clearly defined interfaces. For example, the interaction with the data access layer uses a `ProductsDAO` interface:

```c#
namespace ServerlessTestApi.Core.DataAccess
{
    public interface ProductsDAO
    {
        Task<Product> GetProduct(string id);

        Task PutProduct(Product product);

        Task DeleteProduct(string id);

        Task<ProductWrapper> GetAllProducts();
    }
}
```
This is a simple CRUD API following a Repository pattern. This provides a lightweight core layer. However, this is a valuable separation to have as the application grows.

### ServerlessTestApi.Integrations

This project contains all code that handles integrations your application has. This includes databases, caches, 3rd party API's. All implementation logic is stored in this one library.

In this case, the implementation of our data access layer to interact with Amazon DynamoDB is included here

```c#
namespace ServerlessTestApi.Infrastructure.DataAccess
{
    public class DynamoDbProducts : ProductsDAO
    {
        private static string PRODUCT_TABLE_NAME = Environment.GetEnvironmentVariable("PRODUCT_TABLE_NAME");
        private readonly AmazonDynamoDBClient _dynamoDbClient;

        public DynamoDbProducts()
        {
            this._dynamoDbClient = new AmazonDynamoDBClient();
        }
        
        public async Task<Product> GetProduct(string id)
        {
            var getItemResponse = await this._dynamoDbClient.GetItemAsync(new GetItemRequest(PRODUCT_TABLE_NAME,
                new Dictionary<string, AttributeValue>(1)
                {
                    {ProductMapper.PK, new AttributeValue(id)}
                }));

            return getItemResponse.IsItemSet ? ProductMapper.ProductFromDynamoDB(getItemResponse.Item) : null;
        }

        public async Task PutProduct(Product product)
        {
            await this._dynamoDbClient.PutItemAsync(PRODUCT_TABLE_NAME, ProductMapper.ProductToDynamoDb(product));
        }

        public async Task DeleteProduct(string id)
        {
            await this._dynamoDbClient.DeleteItemAsync(PRODUCT_TABLE_NAME, new Dictionary<string, AttributeValue>(1)
            {
                {ProductMapper.PK, new AttributeValue(id)}
            });
        }

        public async Task<ProductWrapper> GetAllProducts()
        {
            var data = await this._dynamoDbClient.ScanAsync(new ScanRequest()
            {
                TableName = PRODUCT_TABLE_NAME,
                Limit = 20
            });

            var products = new List<Product>();

            foreach (var item in data.Items)
            {
                products.Add(ProductMapper.ProductFromDynamoDB(item));
            }

            return new ProductWrapper(products);
        }
    }
}
```

### Lambda Functions

Outside of these two shared libraries, there is then a separate project per Lambda function. This provides a clear separation of concerns and ensures the functions have a single purpose.

The way we initialize our Lambda function is important for testing. The Lambda service always requires a parameterless constructor for initialization. However, all our function initialization logic is included in an internal constructor. This allows mock implementations to be used for testing.    

```c#
namespace GetProducts
{
    public class Function
    {
        private readonly ProductsDAO dataAccess;
        
        public Function() : this(null)
        {
        }

        internal Function(ProductsDAO dataAccess = null)
        {
            this.dataAccess = dataAccess ?? Startup.ServiceProvider.GetRequiredService<ProductsDAO>();
        }

        public async Task<APIGatewayHttpApiV2ProxyResponse> FunctionHandler(APIGatewayHttpApiV2ProxyRequest apigProxyEvent,
            ILambdaContext context)
        {
            if (!apigProxyEvent.RequestContext.Http.Method.Equals(HttpMethod.Get.Method))
            {
                return new APIGatewayHttpApiV2ProxyResponse
                {
                    Body = "Only GET allowed",
                    StatusCode = (int)HttpStatusCode.MethodNotAllowed,
                };
            }
    
            context.Logger.LogLine($"Received {apigProxyEvent}");

            var products = await dataAccess.GetAllProducts();
    
            context.Logger.LogLine($"Found {products.Products.Count} product(s)");
    
            return new APIGatewayHttpApiV2ProxyResponse
            {
                Body = JsonSerializer.Serialize(products),
                StatusCode = 200,
                Headers = new Dictionary<string, string> {{"Content-Type", "application/json"}}
            };
        }
    }
}
```

The [InternalsVisibleToAttribute](https://docs.microsoft.com/en-us/dotnet/api/system.runtime.compilerservices.internalsvisibletoattribute?view=net-6.0) then allows us to expose this internal constructor to out unit tests.

```c#
[assembly:InternalsVisibleTo("ApiTests.UnitTest")]
```

[[top]](#dotnet-test-samples)

## Run a unit test using a mock framework
Lambda functions frequently call other AWS or 3rd party services. Mock frameworks are useful to simulate service responses. Mock frameworks can speed the development process by enabling rapid feedback iterations. Mocks can be particularly useful for testing failure cases when testing these branches of logic are difficult to do in the cloud.

This project demonstrates how to run tests on both our core business logic, and also for unit testing our Lambda function code itself.

The project uses [xUnit](https://xunit.net/) as the test framework and [Moq](https://github.com/moq/moq4) to provide mocking.

### Unit Testing Lambda Functions

As this is a simple CRUD API the project does not contain any complex business logic. However, we can still write unit tests to validate the execution of our Lambda functions using mocks.

```c#
[Fact]
public async Task TestLambdaHandlerForGetProducts_ShouldReturnSuccess()
{
    var apiRequest = new ApiRequestBuilder()
        .WithHttpMethod("GET")
        .Build();
    
    var mockDataAccessLayer = new Mock<ProductsDAO>();
    mockDataAccessLayer.Setup(p => p.GetAllProducts()).ReturnsAsync(new ProductWrapper());
    
    var function = new Function(mockDataAccessLayer.Object, _mockLogger.Object);

    var result = await function.FunctionHandler(apiRequest, new TestLambdaContext());

    result.StatusCode.Should().Be(200);

    var responseBody = JsonSerializer.Deserialize<ProductWrapper>(result.Body);

    responseBody.Should().NotBeNull();
    responseBody.Products.Count.Should().Be(0);
}
```

Using Moq, it is possible to create a Mock implementation of any object. Once mocked, it is possible to setup how different methods will be invoked.

In this example, a mock implementation of the `ProductsDAO` is added that will be invoked. The It.IsAny<string>() line determines which parameters will cause this mock to be invoked. In this case, if any string is passed into the method this mock will be invoked. The ReturnsAsync method then allows us to define what will be be returned by the mock. In this instance, we are returning an empty `ProductWrapper` object.

The example also uses the builder pattern to generate the API request object to be passed into the function handler.

```c#
public class ApiRequestBuilder
{
    private APIGatewayHttpApiV2ProxyRequest _request;
    private string httpMethod;
    private string body;
    private Dictionary<string, string> headers;

    public ApiRequestBuilder()
    {
        this._request = new APIGatewayHttpApiV2ProxyRequest();
    }

    public ApiRequestBuilder WithHttpMethod(string methodName)
    {
        this.httpMethod = methodName;
        return this;
    }

    public ApiRequestBuilder WithBody(string body)
    {
        this.body = body;
        return this;
    }

    public ApiRequestBuilder WithBody(object body)
    {
        this.body = JsonSerializer.Serialize(body);
        return this;
    }

    public ApiRequestBuilder WithHeaders(Dictionary<string, string> headers)
    {
        this.headers = headers;
        return this;
    }

    public APIGatewayHttpApiV2ProxyRequest Build()
    {
        this._request = new APIGatewayHttpApiV2ProxyRequest()
        {
            RequestContext = new APIGatewayHttpApiV2ProxyRequest.ProxyRequestContext()
            {
                Http = new APIGatewayHttpApiV2ProxyRequest.HttpDescription()
                {
                    Method = httpMethod
                }
            },
            Body = body,
            Headers = headers
        };

        return this._request;
    }
}
```
Another useful feature of Moq is the ability to test exceptions. In the below example, instead of mocking the response of the method call an Exception is thrown. This allows a test to be written to understand what would happen if the S3 SDK threw an exception.  

```c#
[Fact]
public async Task TestLambdaHandlerForGetProducts_ErrorInDataAccess_ShouldReturn500()
{
    var apiRequest = new ApiRequestBuilder()
        .WithHttpMethod("GET")
        .Build();
    
    var mockDataAccessLayer = new Mock<ProductsDAO>();
    mockDataAccessLayer.Setup(p => p.GetAllProducts())
        .ThrowsAsync(new NullReferenceException());
    
    var function = new Function(mockDataAccessLayer.Object, _mockLogger.Object);

    var result = await function.FunctionHandler(apiRequest, new TestLambdaContext());

    result.StatusCode.Should().Be(500);
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
dotnet-test-samples$ AWS_SAM_STACK_NAME=<stack-name> 
dotnet test .\tests\ServerlessTestSamples.IntegrationTest\
```

The sample integration test is straightforward. The [Setup.cs](./tests/ApiTests.IntegrationTest/Setup.cs) is performed using the [class fixture feature of xUnit.](https://xunit.net/docs/shared-context) Class fixtures allow code to be executed once and then shared between all unit tests. In this example, we use the class fixture to retrive the API url and store that in a static variable. This class fixture could be used to create any hardcoded resources to use for testing. The Setup class also implements IDisposable, meaning any test cleanup can be executed in the Dispose() method. In this case, test records are deleted from DynamoDB.

```c#
public class Setup : IDisposable
{
    public static string ApiUrl { get; set; }
    
    private static string _tableName { get; set; }

    // Create a static list of strings to keep track of products IDs that are createdd
    public static List<string> CreatedProductIds { get; } = new List<string>();

    private AmazonDynamoDBClient _dynamoDbClient;

    public Setup()
    {
        var stackName = Environment.GetEnvironmentVariable("AWS_SAM_STACK_NAME") ?? "dotnet-api-test-samples";
        var region = Environment.GetEnvironmentVariable("AWS_SAM_REGION_NAME") ?? "us-east-1";

        if (string.IsNullOrEmpty(stackName))
        {
            throw new Exception("Cannot find env var AWS_SAM_STACK_NAME. Please setup this environment variable with the stack name where we are running integration tests.");
        }

        var cloudFormationClient = new AmazonCloudFormationClient(new AmazonCloudFormationConfig()
        {
            RegionEndpoint = RegionEndpoint.GetBySystemName(region)
        });

        this._dynamoDbClient = new AmazonDynamoDBClient(new AmazonDynamoDBConfig()
        {
            RegionEndpoint = RegionEndpoint.GetBySystemName(region)
        });

        var response = cloudFormationClient.DescribeStacksAsync(new DescribeStacksRequest()
        {
            StackName = stackName
        }).Result;

        ApiUrl = response.Stacks[0].Outputs.FirstOrDefault(p => p.OutputKey == "ApiUrl").OutputValue;
        _tableName = response.Stacks[0].Outputs.FirstOrDefault(p => p.OutputKey == "TableName").OutputValue;
    }

    public void Dispose()
    {
        foreach (var id in CreatedProductIds)
        {
            try
            {
                var getItem = this._dynamoDbClient.GetItemAsync(_tableName, new Dictionary<string, AttributeValue>()
                {
                    {"id", new AttributeValue(id)}
                }).Result;

                if (getItem.IsItemSet)
                {
                    this._dynamoDbClient.DeleteItemAsync(_tableName, new Dictionary<string, AttributeValue>()
                    {
                        {"id", new AttributeValue(id)}
                    }).Wait();
                }
            }
            catch (ResourceNotFoundException)
            {
            }
            catch (HttpErrorResponseException)
            {
            }
        }
    }
}
```

Once the API Url has been set, we can then use that in an integration test to ensure the code works as expected.

```c#
[Fact]
public async Task GetProducts_ShouldReturnSuccess()
{
    var createOrderResult = await _apiDriver.GetProducts();

    createOrderResult.Products.Should().NotBeNull();
}
```

This example uses an `ApiDriver` class to centralise all of the communication with the API, ease re-use and simplify future changes to API schemas/paths. Notice how the API driver class adds the `product.id` to `Setup.CreatedProductIds` on creation, and also removes it on delete.

```c#
internal class ApiDriver
{
    private HttpClient _httpClient;

    public ApiDriver()
    {
        _httpClient = new HttpClient();
        _httpClient.DefaultRequestHeaders.Add("INTEGRATION_TEST", "true");
    }

    public async Task<ProductWrapper> GetProducts()
    {
        var result = await _httpClient.GetAsync($"{Setup.ApiUrl}");

        result.StatusCode.Should().Be(HttpStatusCode.OK);

        return JsonSerializer.Deserialize<ProductWrapper>(await result.Content.ReadAsStringAsync());
    }

    public async Task<Product> GetProduct(string id, HttpStatusCode expectedStatusCode = HttpStatusCode.OK)
    {
        var result = await _httpClient.GetAsync($"{Setup.ApiUrl}{id}");

        result.StatusCode.Should().Be(expectedStatusCode);

        if (expectedStatusCode != HttpStatusCode.OK)
        {
            return null;
        }

        return JsonSerializer.Deserialize<Product>(await result.Content.ReadAsStringAsync());
    }

    public async Task<string> CreateProduct(Product product)
    {
        var result = await _httpClient.PutAsync($"{Setup.ApiUrl}{product.Id}", new StringContent(JsonSerializer.Serialize(product), Encoding.UTF8, "application/json"));

        result.StatusCode.Should().Be(HttpStatusCode.Created);

        Setup.CreatedProductIds.Add(product.Id);

        return await result.Content.ReadAsStringAsync();
    }

    public async Task<string> DeleteProduct(string id)
    {
        var result = await _httpClient.DeleteAsync($"{Setup.ApiUrl}{id}");

        result.StatusCode.Should().Be(HttpStatusCode.OK);
        
        Setup.CreatedProductIds.Remove(id);

        return await result.Content.ReadAsStringAsync();
    }
}
```

[[top]](#dotnet-test-samples)

## Use SAM Accerate to speed up feedback cycles
AWS SAM Accelerate is a set of features that reduces deployment latency and enable developers to test their code quickly against production AWS services in the cloud.
[Read the blog post](https://aws.amazon.com/blogs/compute/accelerating-serverless-development-with-aws-sam-accelerate/)

```bash
# synchronize local code with the cloud
dotnet-test-samples$ sam sync --watch --stack-name dotnet-api-test-samples
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

## Cleanup

To delete the sample application that you created, use the SAM CLI.

```bash
sam delete
```

## Additional Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

Next, you can use AWS Serverless Application Repository to deploy ready to use Apps that go beyond hello world samples and learn how authors developed their applications: [AWS Serverless Application Repository main page](https://aws.amazon.com/serverless/serverlessrepo/)
