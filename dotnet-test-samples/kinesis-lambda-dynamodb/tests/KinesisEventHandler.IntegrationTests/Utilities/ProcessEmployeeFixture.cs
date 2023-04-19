using System.Text;
using System.Text.Json;
using Amazon;
using Amazon.CloudFormation;
using Amazon.CloudFormation.Model;
using Amazon.DynamoDBv2;
using Amazon.Kinesis;
using Amazon.Kinesis.Model;
using AWS.Lambda.Powertools.Logging;
using KinesisEventHandler.Models;
using KinesisEventHandler.Repositories;
using Microsoft.Extensions.Options;
using Xunit;

namespace KinesisEventHandler.IntegrationTests.Utilities;

public class ProcessEmployeeFixture : IAsyncLifetime
{
    private string _employeeRecordsStreamName = null!;
    private const string Source = "kinesis-event-handler-test";
    public List<string> CreatedEmployeeIds { get; } = new();
    public EmployeeRepository? TestEmployeeRepository;
    public AmazonKinesisClient KinesisClient = null!;

    public async Task InitializeAsync()
    {
        var stackName = Environment.GetEnvironmentVariable("AWS_SAM_STACK_NAME") ?? "kinesis-lambda-dynamodb";
        var region = Environment.GetEnvironmentVariable("AWS_SAM_REGION_NAME") ?? "us-east-1";
        var endpoint = RegionEndpoint.GetBySystemName(region);
        var cloudFormationClient =
            new AmazonCloudFormationClient(new AmazonCloudFormationConfig() { RegionEndpoint = endpoint });
        var response =
            await cloudFormationClient.DescribeStacksAsync(new DescribeStacksRequest() { StackName = stackName });
        var outputs = response.Stacks[0].Outputs;
        
        Console.WriteLine(outputs);

        KinesisClient = new AmazonKinesisClient(region: endpoint);
        var dynamoDbClient = new AmazonDynamoDBClient(new AmazonDynamoDBConfig() { RegionEndpoint = endpoint });
        var options = Options.Create(new DynamoDbOptions
        {
            EmployeeStreamTableName = GetOutputVariable(outputs, "EmployeeStreamTableName")
        });
        TestEmployeeRepository = new EmployeeRepository(dynamoDbClient, options);

        _employeeRecordsStreamName = GetOutputVariable(outputs, "EmployeeRecordsStream");
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

    public async Task<PutRecordResponse> StreamRecordAsync(Employee employee)
    {
        var dataBytes = Encoding.UTF8.GetBytes(JsonSerializer.Serialize(employee));

        using var ms = new MemoryStream(dataBytes);
        var request = new PutRecordRequest
        {
            StreamName = _employeeRecordsStreamName,
            PartitionKey = Source,
            Data = ms
        };

        Console.WriteLine(
            $"Source: {Source}, writing Employee: {employee.EmployeeId} to Kinesis Stream: {_employeeRecordsStreamName}");

        var response = await KinesisClient.PutRecordAsync(request);

        Console.WriteLine(
            $"Sequence number {response.SequenceNumber}, ShardId: {response.ShardId}");

        return response;
    }

    private static string GetOutputVariable(IEnumerable<Output> outputs, string name) =>
        outputs.FirstOrDefault(o => o.OutputKey == name)?.OutputValue
        ?? throw new Exception($"CloudFormation stack does not have an output variable named '{name}'");
}