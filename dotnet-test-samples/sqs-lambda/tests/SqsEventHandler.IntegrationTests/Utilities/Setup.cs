using Amazon;
using Amazon.CloudFormation;
using Amazon.CloudFormation.Model;
using Amazon.DynamoDBv2;
using Amazon.SQS;
using Amazon.SQS.Model;
using AWS.Lambda.Powertools.Logging;
using Microsoft.Extensions.Options;
using SqsEventHandler.Repositories;
using Xunit;

namespace SqsEventHandler.IntegrationTests.Utilities;

public class Setup : IAsyncLifetime
{
    public string? SqsEventQueueUrl;
    public List<string> CreatedEmployeeIds { get; } = new();
    public EmployeeRepository? TestEmployeeRepository;

    public async Task InitializeAsync()
    {
        var stackName = Environment.GetEnvironmentVariable("AWS_SAM_STACK_NAME") ?? "sqs-lambda";
        var region = Environment.GetEnvironmentVariable("AWS_SAM_REGION_NAME") ?? "us-east-1";
        var endpoint = RegionEndpoint.GetBySystemName(region);
        var cloudFormationClient =
            new AmazonCloudFormationClient(new AmazonCloudFormationConfig() { RegionEndpoint = endpoint });
        var response =
            await cloudFormationClient.DescribeStacksAsync(new DescribeStacksRequest() { StackName = stackName });
        var outputs = response.Stacks[0].Outputs;

        var dynamoDbClient = new AmazonDynamoDBClient(new AmazonDynamoDBConfig() { RegionEndpoint = endpoint });
        var options = Options.Create(new DynamoDbOptions
        {
            EmployeeTableName = GetOutputVariable(outputs, "EmployeeTableName")
        });
        TestEmployeeRepository = new EmployeeRepository(dynamoDbClient, options);

        SqsEventQueueUrl = GetOutputVariable(outputs, "ProcessEmployeeQueueUrl");
    }

    public async Task DisposeAsync()
    {
        foreach (var employeeId in CreatedEmployeeIds)
        {
            try
            {
                await TestEmployeeRepository!.DeleteItemAsync(employeeId, CancellationToken.None);
            }
            catch (Exception ex)
            {
                Logger.LogCritical(ex);
            }
        }
    }

    public async Task<SendMessageResponse> SendMessageAsync(IAmazonSQS sqsClient, string? qUrl, string? messageBody)
    {
        return await sqsClient.SendMessageAsync(qUrl, messageBody);
    }

    private static string GetOutputVariable(IEnumerable<Output> outputs, string name) =>
        outputs.FirstOrDefault(o => o.OutputKey == name)?.OutputValue
        ?? throw new Exception($"CloudFormation stack does not have an output variable named '{name}'");
}