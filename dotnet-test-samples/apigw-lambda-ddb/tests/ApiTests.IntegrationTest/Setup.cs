using Amazon;
using Amazon.CloudFormation;
using Amazon.CloudFormation.Model;
using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.Model;
using Amazon.Runtime.Internal;

namespace ApiTests.IntegrationTest;

public class Setup : IDisposable
{
    public static string ApiUrl { get; set; }
    
    private static string _tableName { get; set; }

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