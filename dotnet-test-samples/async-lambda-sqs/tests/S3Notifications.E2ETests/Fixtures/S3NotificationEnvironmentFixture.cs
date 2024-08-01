using Amazon;
using Amazon.CloudFormation;
using Amazon.CloudFormation.Model;
using Amazon.S3;
using Amazon.S3.Model;
using Amazon.SQS;
using Xunit;

namespace S3Notifications.E2ETests.Fixtures;

public class S3NotificationEnvironmentFixture : IAsyncLifetime, IDisposable
{
    private readonly RegionEndpoint _regionEndpoint;
    public IAmazonS3 S3Client { get; }
    public IAmazonSQS SqsClient { get; }

    public string BucketName { get; private set; } = null!;
    internal string SqsQueueUrl { get; set; } = null!;

    public S3NotificationEnvironmentFixture()
    {
        var regionName = Environment.GetEnvironmentVariable("AWS_SAM_REGION_NAME") ?? "eu-west-2";

        _regionEndpoint = RegionEndpoint.GetBySystemName(regionName);

        S3Client = new AmazonS3Client(_regionEndpoint);
        SqsClient = new AmazonSQSClient(_regionEndpoint);
    }

    public void Dispose()
    {
        S3Client.Dispose();
        SqsClient.Dispose();
    }

    public async Task InitializeAsync()
    {
        var stackName = Environment.GetEnvironmentVariable("AWS_SAM_STACK_NAME") ?? "async-sqs";
        using var cloudFormationClient = new AmazonCloudFormationClient(
            new AmazonCloudFormationConfig
            {
                RegionEndpoint = _regionEndpoint
            });

        var describeStacksResponse = await cloudFormationClient.DescribeStacksAsync(new DescribeStacksRequest
        {
            StackName = stackName
        });

        var stackOutputs = describeStacksResponse.Stacks.First().Outputs;
        BucketName = stackOutputs.First(x => x.OutputKey == "S3BucketName")
            .OutputValue;
        
        SqsQueueUrl = stackOutputs.First(x => x.OutputKey == "QueueUrl")
            .OutputValue;
    }

    public async Task DisposeAsync()
    {
        // list all files in S3 bucket then delete them
        var listObjectsRequest = new ListObjectsV2Request
        {
            BucketName = BucketName
        };
        
        var listFilesResponse = await S3Client.ListObjectsV2Async(listObjectsRequest);

        foreach (var s3Object in listFilesResponse.S3Objects)
        {
            await S3Client.DeleteObjectAsync(new DeleteObjectRequest
            {
                BucketName = BucketName,
                Key = s3Object.Key
            });
        }

        await SqsClient.PurgeQueueAsync(SqsQueueUrl);
    }
    
}