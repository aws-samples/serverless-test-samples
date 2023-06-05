namespace AsyncTesting.IntegrationTest;

using Amazon;
using Amazon.CloudFormation;
using Amazon.CloudFormation.Model;
using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.Model;
using Amazon.S3;
using Amazon.S3.Model;

public class Setup : IAsyncLifetime
{
    public IAmazonDynamoDB DynamoDbClient { get; set; } = null!;

    public IAmazonS3 S3Client { get; set; } = null!;

    public string SourceBucketName { get; set; } = null!;

    public string DestinationBucketName { get; set; } = null!;
    
    public string DestinationTableName { get; set; } = null!;

    public List<string> CreatedFiles { get; set; } = new();

    public async Task InitializeAsync()
    {
        var stackName = Environment.GetEnvironmentVariable("AWS_SAM_STACK_NAME") ?? "async-testing";
        var region = Environment.GetEnvironmentVariable("AWS_SAM_REGION_NAME") ?? "eu-west-1";
        var endpoint = RegionEndpoint.GetBySystemName(region);
        var cloudFormationClient = new AmazonCloudFormationClient(new AmazonCloudFormationConfig() { RegionEndpoint = endpoint });
        var response = await cloudFormationClient.DescribeStacksAsync(new DescribeStacksRequest() { StackName = stackName });
        var outputs = response.Stacks[0].Outputs;

        SourceBucketName = GetOutputVariable(outputs, "SourceBucketName");
        DestinationTableName = GetOutputVariable(outputs, "AsyncTransformTestResultsTable");
        DynamoDbClient = new AmazonDynamoDBClient(new AmazonDynamoDBConfig() { RegionEndpoint = endpoint });
        S3Client = new AmazonS3Client(new AmazonS3Config() { RegionEndpoint = endpoint });
    }

    public async Task DisposeAsync() {
        foreach (var file in CreatedFiles)
        {
            await this.S3Client.DeleteObjectAsync(
                new DeleteObjectRequest()
                {
                    BucketName = this.SourceBucketName,
                    Key = file
                });

            try
            {
                await this.S3Client.DeleteObjectAsync(
                    new DeleteObjectRequest()
                    {
                        BucketName = this.DestinationBucketName,
                        Key = file
                    });
            }
            catch (Exception)
            {
                // Catch errors in case file does not exist
            }

            try
            {
                await this.DynamoDbClient.DeleteItemAsync(
                    this.DestinationTableName,
                    new Dictionary<string, AttributeValue>(1)
                    {
                        { "id", new AttributeValue(file) }
                    });
            }
            catch (Exception)
            {
                // Catch errors in case record is not written to DynamoDB table
            }
        }
    }

    private static string GetOutputVariable(List<Output> outputs, string name) =>
        outputs.FirstOrDefault(o => o.OutputKey == name)?.OutputValue
        ?? throw new Exception($"CloudFormation stack does not have an output variable named '{name}'");
}