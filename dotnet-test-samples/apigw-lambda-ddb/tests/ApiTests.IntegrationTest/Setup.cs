using Amazon;
using Amazon.CloudFormation;
using Amazon.CloudFormation.Model;
using Amazon.DynamoDBv2;

namespace ApiTests.IntegrationTest;

public class Setup : IAsyncLifetime
{
    private string? _tableName;
    private AmazonDynamoDBClient? _dynamoDbClient;

    public string ApiUrl { get; private set; } = default!;

    public List<string> CreatedProductIds { get; } = new();

    public async Task InitializeAsync()
    {
        var stackName = Environment.GetEnvironmentVariable("AWS_SAM_STACK_NAME") ?? "dotnet-api-test-samples";
        var region = Environment.GetEnvironmentVariable("AWS_SAM_REGION_NAME") ?? "us-east-1";
        var endpoint = RegionEndpoint.GetBySystemName(region);
        var cloudFormationClient = new AmazonCloudFormationClient(new AmazonCloudFormationConfig() { RegionEndpoint = endpoint });
        var response = await cloudFormationClient.DescribeStacksAsync(new DescribeStacksRequest() { StackName = stackName });
        var outputs = response.Stacks[0].Outputs;

        ApiUrl = GetOutputVariable(outputs, "ApiUrl");
        _tableName = GetOutputVariable(outputs, "TableName");
        _dynamoDbClient = new AmazonDynamoDBClient(new AmazonDynamoDBConfig() { RegionEndpoint = endpoint });
    }

    public async Task DisposeAsync()
    {
        foreach (var id in CreatedProductIds)
        {
            try
            {
                await _dynamoDbClient!.DeleteItemAsync(_tableName!, new() { ["id"] = new(id) });
            }
            catch
            {
            }
        }
    }

    private static string GetOutputVariable(List<Output> outputs, string name) =>
        outputs.FirstOrDefault(o => o.OutputKey == name)?.OutputValue
        ?? throw new Exception($"CloudFormation stack does not have an output variable named '{name}'");
}