[![.NET: 6.0](https://img.shields.io/badge/.NET-6.0-Green)]()
[![AWS: Lambda](https://img.shields.io/badge/AWS-Lambda-blueviolet)]()
[![Amazon: Api Gateway](https://img.shields.io/badge/Amazon-API%20Gateway-blueviolet)]()
[![Amazon: DynamoDB](https://img.shields.io/badge/Amazon-DynamoDB-blueviolet)]()
[![test: unit](https://img.shields.io/badge/Test-Unit-blue)]()
[![test: integration](https://img.shields.io/badge/Test-Integration-yellow)]()


## DynamoDB Testing using TestContainers & DynamoDB Local

### Description

This pattern creates an Amazon API Gateway HTTP API, an AWS Lambda function, and a DynamoDB Table using SAM and .NET 6. It also demonstrates how you can use a local emulated version of DynamoDB to increase the speed of feedback loops as you make changes to your application code.

Important: this application uses various AWS services and there are costs associated with these services after the Free Tier usage. Please see the AWS Pricing page for details. You are responsible for any AWS costs incurred.

## Language
.NET 6

## Framework
The framework used to deploy the infrastructure is SAM

## Services used
The AWS services used in this pattern are

*API Gateway - AWS Lambda - DynamoDB*

## Prerequisites
The ability to run Docker containers on your local machine.

## Topology

<img src="./img/apigw-lambda-ddb.jpg" alt="topology" width="80%"/>


## Description
The SAM template contains all the information to deploy AWS resources (an API Gateway, 4 Lambda functions and a DynamoDB table) and also the permission required by these services to communicate.

You will be able to create and delete the CloudFormation stack using the SAM CLI.

After the stack is created you can access the follow routes on the API to perform different CRUD actions:

### GET /

List all products in the database.

### GET /{id}

Retrieve a specific product from the database.

### PUT /{id}

Create or update a product in the database, the API expects the below payload:

```json
{
    "Id": "my-unique-id",
    "Name": "Test Product",
    "Price": 10
}
```

### DELETE /{id}

Deletes an existing product.

## Project Structure

The application follows Clean/Hexagonal/Ports & Adapters Architecture principles. This means core business logic has no external dependencies and all integrations are pushed to the outside. The solution is split down into 3 projects:

- [ServerlessTestApi.Core](./src/ServerlessTestApi.Core/) *Contains all core business/domain logic*
- [ServerlessTestApi.Infrastructure](./src/ServerlessTestApi.Core/) *Contains code for any integrations, in this case DynamoDB*
- Function projects:
    - [GetProducts](./src/GetProducts/)
    - [GetProduct](./src/GetProduct/)
    - [PutProduct](./src/PutProduct/)
    - [DeleteProduct](./src/DeleteProduct/)

Any integrations required by the Core layer are abstracted behind an interface, for example:

```c#
namespace ServerlessTestApi.Core.DataAccess;

public interface ProductsDAO
{
    Task<ProductDTO> GetProduct(string id, CancellationToken cancellationToken);

    Task PutProduct(Product product, CancellationToken cancellationToken);

    Task DeleteProduct(string id, CancellationToken cancellationToken);

    Task<ProductWrapper> GetAllProducts(CancellationToken cancellationToken);
}
```

This enables easy mocking.

## Deployment commands

The AWS SAM CLI is used to deploy the application. When working through the `sam deploy --guided` take note of the stack name used.

````
sam init
sam build
sam deploy --guided
````

## Testing

To test the endpoint, first send data using the following command. Be sure to update the URL with the endpoint of your stack.

```
curl -X POST https://{ApiUrl}/dev/a-unique-product-id -H "Content-Type: application/json" -d '{"Id": "a-unique-product-id", "Name": "Test Product", "Price": 10}' 
```

## Automated Tests
The source code for this sample includes automated unit and integration tests. [xUnit](https://xunit.net/) is the primary test framework used to write these tests. A few other libraries and frameworks are used depending on the test case pattern. Please see below.

### Unit Tests ([MockPutProductFunctionTests.cs](tests/ApiTests.UnitTest/MockPutProductFunctionTests.cs))
The goal of these tests is to run a unit test on the handler method of the Lambda functions. It uses [FakeItEasy](https://github.com/FakeItEasy/FakeItEasy) for the mocking framework. The `ProductsDAO` interface is faked.

These tests also demonstrate how you can use emulation using [DynamoDB Local](https://github.com/awslabs/amazon-dynamodb-local-samples) and the [TestContainers](https://testcontainers.com/) project to startup, initialize and tear down an emulated version of DynamoDB for the purpose of local testing.

The tests use a combination of emulation, to test happy paths. And mocking to test for service exceptions and other errors.

The startup of the emulator is found in the [TestStartup.cs](./tests/ApiTests.UnitTest/TestStartup.cs) file. The emulated instance of DynamoDB is started up using the `DynamoDBBuilder` class, and port 8000 from the container is mapped to a random port on the local machine. 

```c#
container = new DynamoDbBuilder()
    .WithPortBinding(
        8000,
        true)
    .Build();

container.StartAsync().GetAwaiter().GetResult();

var serviceUrl = $"http://localhost:{container.GetMappedPublicPort(8000)}";

var dynamoDbClient = new AmazonDynamoDBClient(new BasicAWSCredentials("test", "test"),
    new AmazonDynamoDBConfig()
    {
        ServiceURL = serviceUrl,
    });
```

As part of the startup code, the DynamoDB table is created and a sample `Product` is added to the database:

```c#
var createReq = new CreateTableRequest(
    "Products",
    new List<KeySchemaElement>()
    {
        new KeySchemaElement(
            "id",
            KeyType.HASH)
    });
createReq.AttributeDefinitions = new List<AttributeDefinition>(1)
{
    new AttributeDefinition(
        "id",
        ScalarAttributeType.S)
};
createReq.BillingMode = BillingMode.PAY_PER_REQUEST;

dynamoDbClient.CreateTableAsync(createReq).GetAwaiter().GetResult();

this.ProductsDao = new DynamoDbProducts(dynamoDbClient, Options.Create(new DynamoDbOptions()
{
    ProductTableName = "Products"
}));

this.TestProduct = new Product(
    Guid.NewGuid().ToString(),
    "TestProduct",
    10);

this.ProductsDao.PutProduct(this.TestProduct, default)
    .GetAwaiter()
    .GetResult();
```

Finally, the test classes themselves inject the `TestStartup` object using the `CollectionFixture` feature of xUnit. That allows the initialized `ProductsDAO` instance to be used throughout the test cases. 

```c#
public MockPutProductFunctionTests(TestStartup startup)
{
    this._startup = startup;
}

[Fact]
public async Task PutProduct_WithSuccessfulInsert_Should_Return201()
{
    // arrange
    var dto = new ProductDTO("testcreateid", "test product", 10);
    var request = new ApiRequestBuilder()
        .WithHttpMethod(HttpMethod.Put)
        .WithBody(dto)
        .WithPathParameter("id", dto.Id)
        .Build();
    
    var function = new Function(this._startup.ProductsDao, Logger, JsonOptions);

    // act
    var response = await function.FunctionHandler(request, new TestLambdaContext());

    // assert
    Assert.Multiple(
        () => response.StatusCode.Should().Be(201),
        () => response.Headers["Location"].Should().Be("https://localhost/dev/testcreateid")
    );
}
```

A custom class following the builder pattern is used to [build the API request](./tests/ApiTests.UnitTest/ApiRequestBuilder.cs) to be sent into the handler.

To execute the tests:

**Powershell**
```powershell
dotnet test tests\ApiTests.UnitTest\ApiTests.UnitTest.csproj
```
**Bash**
```powershell
dotnet test tests/ApiTests.UnitTest/ApiTests.UnitTest.csproj
```

### Integration Tests ([IntegrationTest.cs](./tests/ApiTests.IntegrationTest/IntegrationTest.cs))
The goal of this test is to demonstrate a test that runs the Lambda function's code against deployed resources. The tests interact with the API endpoints directly and tests the expected responses returned by the API. Before running these tests, resources will need to be deployed using the steps in the `Deployment Commands` section above. Tests are there for both happy and sad paths.

It uses the [IClassFixture](https://xunit.net/docs/shared-context) feature of [xUnit](https://xunit.net/) to perform [setup](./tests/ApiTests.IntegrationTest/Setup.cs) and teardown logic. The [setup](./tests/ApiTests.IntegrationTest/Setup.cs) code retrieves the API URL and DynamoDB table name from the deployed CloudFormation stack. Teardown code ensures all created Product Ids are deleted from the table.

The tests themselves make API calls directly to the deployed resource.

To execute the tests:

**Powershell**
```powershell
$env:AWS_SAM_STACK_NAME = <STACK_NAME_USED_IN_SAM_DEPLOY>
$env:AWS_SAM_REGION_NAME = <REGION_NAME_USED_IN_SAM_DEPLOY>
dotnet test .\tests\ApiTests.IntegrationTest\ApiTests.IntegrationTest.csproj
```

**Bash**
```bash
AWS_SAM_STACK_NAME=<STACK_NAME_USED_IN_SAM_DEPLOY>
AWS_SAM_REGION_NAME=<REGION_NAME_USED_IN_SAM_DEPLOY>
dotnet test ./tests/ApiTests.IntegrationTest/ApiTests.IntegrationTest.csproj
```

## Cleanup

Run the given command to delete the resources that were created. It might take some time for the CloudFormation stack to get deleted.
```
sam delete
```

## Requirements

* [Create an AWS account](https://portal.aws.amazon.com/gp/aws/developer/registration/index.html) if you do not already have one and log in. The IAM user that you use must have sufficient permissions to make necessary AWS service calls and manage AWS resources.
* [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) installed and configured
* [Git Installed](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
* [AWS Serverless Application Model](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) (AWS SAM) installed
* [.NET 6](https://dotnet.microsoft.com/en-us/download/dotnet/6.0) installed
* The ability to run Docker containers

## Video Walkthroughs

[Testcontainers with .NET](https://www.youtube.com/watch?v=z0F9tofV_MQ)