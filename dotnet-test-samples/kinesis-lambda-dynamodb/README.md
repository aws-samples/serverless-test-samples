[![Built with: .Net 6](https://img.shields.io/badge/Microsoft-.Net%206-blue?style=plastic&logo=microsoft)](https://learn.microsoft.com/en-us/dotnet/core/introduction)
[![AWS: Kinesis](https://img.shields.io/badge/Amazon-Kinesis-blueviolet?style=plastic&logo=amazonaws)]()
[![AWS: Lambda](https://img.shields.io/badge/AWS-Lambda-orange?style=plastic&logo=amazonaws)]()
[![AWS: DynamoDB](https://img.shields.io/badge/Amazon-DynamoDB-darkblue?style=plastic&logo=amazonaws)]()
[![test: unit](https://img.shields.io/badge/Test-Unit-blue?style=plastic&logo=)]()
[![test: integration](https://img.shields.io/badge/Test-Integration-yellow?style=plastic&logo=)]()

## Amazon Kinesis Data Streams, AWS Lambda Function & Amazon DynamoDB

### Description

This pattern creates an AWS Lambda function that consumes messages from an Amazon Kinesis Data Streams and dumps them to Amazon DynamoDB using SAM and .NET 6.

> **Important:** *This application uses various AWS services and there are costs associated with these services after the Free Tier usage. Please see the AWS Pricing page for details. You are responsible for any AWS costs incurred.*

## Language
.NET 6

## Framework
The framework used to deploy the infrastructure is [SAM](https://aws.amazon.com/serverless/sam)

## Services used
The AWS services used in this pattern are

*Amazon Kinesis  &rarr;  AWS Lambda &rarr; Amazon DynamoDB*

> Amazon DynamoDB is not part of SUT in this pattern

## Topology

### System Under Test (SUT)

The SUT is a streaming data processing system. A Lambda function has an Event Source Mapping to a Kinesis Data Stream. The Lambda Event Source Mapping(ESM) polls the Kinesis Data Stream and then synchronously invokes the Lambda function with a batch of messages. The Lambda function processes batches of messages and writes results to a DynamoDB Table.

![System Under Test (SUT)](../docs/kinesis-system-under-test.png)

### Goal

The goal of this example is to show how to test Lambda functions that are part of a streaming data processing application. In streaming workloads the number of messages that are sent to Lambda in a batch can change with the rate of messages being published to the stream, so we show testing with different sized batches.

### Description

In this pattern you will deploy a streaming workload where a Lambda function is triggered by messages in a Kinesis Data Stream. This project demonstrates several techniques for executing tests including running Lambda function locally with a simulated payload as well integration tests in the cloud.

![System Under Test Description (SUT)](../docs/kinesis-system-under-test-description.png)

This example contains an [Amazon Kinesis Data Stream](https://aws.amazon.com/kinesis/data-streams/), [AWS Lambda](https://aws.amazon.com/lambda/) and [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) table core resources.

The Amazon Kinesis Data Stream can stream data but the AWS Lambda function in this example expects Kinesis Stream Event data to contain a JSON object with 2 properties, `batch` and `id`:

```json
{
    "employee_id": "string",
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "dob": "DateTime",
    "doh": "DateTime"
}
```

- `employee_id`: unique identifier for each individual record. Each record should have a unique `id` property value
- `email`: email address of the employee
- `first_name`: first name of the employee
- `last_name`: last name of the employee
- `dob`: date of birth of the employee
- `doh`: date of hire of the employee

The AWS Lambda function converts the incoming event data into the processed record JSON, setting the `employee_id` to be the DynamoDB Partition Key.

> The SAM template contains all the information to deploy AWS resources (An Amazon Kinesis Data Stream, an AWS Lambda function and an Amazon DynamoDB) and also the permissions required by these services to communicate.

You will be able to create and delete the CloudFormation stack using the SAM CLI.

## Project Structure

The solution is split down into two projects:

- [KinesisEventHandler.Infrastructure](./src/KinesisEventHandler.Infrastructure/KinesisEventHandler.Infrastructure.csproj) _Contains code for bootstrapping the ServiceProvider and extensions._
- [KinesisEventHandler.Repositories](./src/KinesisEventHandler.Repositories/KinesisEventHandler.Repositories.csproj) _Contains code for any persistence layer, in this case DynamoDB._
- Function project(s):
  - [KinesisEventHandler](./src/KinesisEventHandler/KinesisEventHandler.csproj)

- Test project(s):
  - [KinesisEventHandler.UnitTests](./tests/KinesisEventHandler.UnitTests/KinesisEventHandler.UnitTests.csproj)
  - [KinesisEventHandler.IntegrationTests](./tests/KinesisEventHandler.IntegrationTests/KinesisEventHandler.IntegrationTests.csproj)

## Deployment commands

The AWS SAM CLI is used to deploy the application. When working through the `sam deploy --guided` take note of the stack name used.

```
sam build
sam deploy --guided
```

## Testing

To test the application, you need to write a record to the Kinesis Data Stream. This can be done in following ways:

- [AWS SDK for .Net](https://docs.aws.amazon.com/sdkfornet/v3/apidocs/items/Kinesis/MKinesisPutRecordPutRecordRequest.html)

- Put Record API: refer [Amazon Kinesis Streams API Reference](https://docs.aws.amazon.com/kinesis/latest/APIReference/API_PutRecord.html)

  Sample Request:
  ```http request
  POST / HTTP/1.1
    Host: kinesis.<region>.<domain>
    Content-Length: <PayloadSizeBytes>
    User-Agent: <UserAgentString>
    Content-Type: application/x-amz-json-1.1
    Authorization: <AuthParams>
    Connection: Keep-Alive
    X-Amz-Date: <Date>
    X-Amz-Target: Kinesis_20131202.PutRecord
    {
      "StreamName": "exampleStreamName",
      "Data": "XzxkYXRhPl8x",
      "PartitionKey": "partitionKey"
    }
  ```

## Automated Tests
The source code for this sample includes automated unit and integration tests. [xUnit](https://xunit.net/) is the primary test framework used to write these tests. A few other libraries and frameworks are used depending on the test case pattern. Please see below.

### Unit Tests

#### [ProcessEmployeeFunctionTests.cs](./tests/KinesisEventHandler.UnitTests/Functions/ProcessEmployeeFunctionTests.cs)
The goal of these tests is to run a unit test on the `ProcessKinesisRecord` method which is called by the handler method of the Lambda function.
The system under test here is completely abstracted from any cloud resources.

```c#
[Fact]
public Task ProcessEmployeeFunction_Should_ExecuteSuccessfully()
{
    //Arrange
    var repository = new Mock<IDynamoDbRepository<EmployeeDto>>();

    repository.Setup(x =>
            x.PutItemAsync(It.IsAny<EmployeeDto>(), It.IsAny<CancellationToken>()))
        .ReturnsAsync(UpsertResult.Inserted);

    var sut = new ProcessEmployeeFunction(repository.Object);
    var employee = new EmployeeBuilder().Build();
    var context = new TestLambdaContext();

    //Act
    var taskResult = sut.ProcessKinesisRecord(employee, context);

    //Assert
    Assert.True(taskResult.IsCompleted);
    return Task.CompletedTask;
}
```

#### [KinesisEventHandlerTests.cs](./tests/KinesisEventHandler.UnitTests/Handlers/KinesisEventHandlerTests.cs)
The goal of these tests is to run a unit test on the KinesisEventHandler which implements the handler method of the Lambda function.
It uses [Moq](https://github.com/moq/moq4) for the mocking framework. The `PutItemAsync` method in `IDynamoDbRepository` is mocked.

```c#
[Fact]
public async Task KinesisEventHandler_Should_CallProcessKinesisRecordOnce()
{
    //Arrange
    var expected = new EmployeeBuilder().Build();
    var kinesisEvent = new KinesisEventBuilder().WithEmployees(new[] { expected });
    var lambdaContext = new TestLambdaContext();

    //Act
    var result = await _mockKinesisEventTrigger.Object.Handler(kinesisEvent, lambdaContext);

    //Assert
    result.BatchItemFailures.Should().BeEmpty();
    _mockKinesisEventTrigger.Verify(x =>
            x.ProcessKinesisRecord(
                It.Is<Employee>(employee => employee.Equals(expected)),
                It.IsAny<ILambdaContext>()),
        Times.Once);
}
```

To execute the tests:

**Powershell**
```shell
dotnet test tests\KinesisEventHandler.UnitTests\KinesisEventHandler.UnitTests.csproj
```
**Bash**
```shell
dotnet test tests/KinesisEventHandler.UnitTests/KinesisEventHandler.UnitTests.csproj
```

### Integration Tests 

#### [ProcessEmployeeTests.cs](./tests/KinesisEventHandler.IntegrationTests/ProcessEmployeeTests.cs)

The goal of this test is to demonstrate a test that runs the Lambda function's code against deployed resources.
The tests interact with the Kinesis Data Stream directly using [AmazonKinesisClient](https://docs.aws.amazon.com/sdkfornet1/latest/apidocs/html/T_Amazon_Kinesis_AmazonKinesisClient.htm) 
and tests the expected responses returned.

```c#
[Fact, TestPriority(1)]
public async Task WriteToEmployeeRecordsStream_Should_ReturnSuccess()
{
    //Arrange
    var employee = new EmployeeBuilder().WithEmployeeId(EmployeeId);

    //Act
    var response = await _processEmployeeFixture.StreamRecordAsync(employee);

    //Assert
    response.Should().NotBeNull();
    response.HttpStatusCode.Should().Be(HttpStatusCode.OK);
}

[RetryFact(3, 5000), TestPriority(2)]
public async Task WriteToEmployeeRecordsStream_Should_UpsertEmployee()
{
    //Act
    using var cts = new CancellationTokenSource();
    var response = await _processEmployeeFixture.TestEmployeeRepository!
        .GetItemAsync(EmployeeId, cts.Token);

    //Assert
    response.Should().NotBeNull();
    response!.EmployeeId.Should().Be(EmployeeId);
    _testOutputHelper.WriteLine(response.ToString());

    //Dispose
    _processEmployeeFixture.CreatedEmployeeIds.Add(EmployeeId);
}
```

> Before running these tests, resources will need to be deployed using the steps in the `Deployment Commands` section above. Tests are there for both happy and sad paths.

To execute the tests:

**Powershell**
```shell
$env:AWS_SAM_STACK_NAME = <STACK_NAME_USED_IN_SAM_DEPLOY>
$env:AWS_SAM_REGION_NAME = <REGION_NAME_USED_IN_SAM_DEPLOY>
dotnet test ./tests/KinesisEventHandler.IntegrationTests/KinesisEventHandler.IntegrationTests.csproj
```

**Bash**
```shell
AWS_SAM_STACK_NAME=<STACK_NAME_USED_IN_SAM_DEPLOY>
AWS_SAM_REGION_NAME=<REGION_NAME_USED_IN_SAM_DEPLOY>
dotnet test ./tests/KinesisEventHandler.IntegrationTests/KinesisEventHandler.IntegrationTests.csproj 
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