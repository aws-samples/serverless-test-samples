using Amazon;
using Amazon.CloudFormation;
using Amazon.CloudFormation.Model;
using Amazon.S3;
using Amazon.S3.Model;
using Amazon.SQS;
using Amazon.SQS.Model;
using Xunit;

namespace S3Notifications.integrationTests.Fixtures;

public class S3NotificationEnvironmentFixture : IAsyncLifetime, IDisposable
{
    private readonly RegionEndpoint _regionEndpoint;
    public IAmazonS3 S3Client { get; }
    private IAmazonSQS SqsClient { get; }

    public string BucketName { get; private set; } = null!;
    private string SqsQueueUrl { get; set; } = null!;

    public S3NotificationEnvironmentFixture()
    {
        var regionName = Environment.GetEnvironmentVariable("AWS_SAM_REGION_NAME") ?? "us-east-1";

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
        var stackName = Environment.GetEnvironmentVariable("AWS_SAM_STACK_NAME") ?? "async-lambda-sqs";
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
    
    public async Task<Message> GetNextMessage()
    {
        var receiveMessageRequest = new ReceiveMessageRequest
        {
            QueueUrl = SqsQueueUrl,
            MaxNumberOfMessages = 1,
            VisibilityTimeout = 1
        };

        int count = 0;
        ReceiveMessageResponse? receiveMessageResponse = null;
        do
        {
            await Task.Delay(1000);
            receiveMessageResponse = await SqsClient.ReceiveMessageAsync(receiveMessageRequest);
            if (receiveMessageResponse.Messages.Count != 0)
            {
                break;
            }
        } while (count++ < 300);

        Assert.NotNull(receiveMessageResponse);
        Assert.NotEmpty(receiveMessageResponse.Messages);
            
        var message = receiveMessageResponse.Messages[0];
        await SqsClient.DeleteMessageAsync(SqsQueueUrl, message.ReceiptHandle);
            
        return message;
    }
}