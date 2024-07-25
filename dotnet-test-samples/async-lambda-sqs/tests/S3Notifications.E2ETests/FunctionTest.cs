using System.Text.Json;
using Amazon.S3;
using Amazon.S3.Model;
using Amazon.SQS;
using S3Notifications.E2ETests.Fixtures;
using S3Notifications.TestUtilities.Extensions;
using Xunit;

namespace S3Notifications.E2ETests;

public class FunctionTest : 
    IClassFixture<S3NotificationEnvironmentFixture>
{
    private readonly IAmazonS3 _s3Client;
    private readonly string _bucketName;
    private readonly IAmazonSQS _sqsClient;
    private readonly string _sqsQueueUrl;

    public FunctionTest(S3NotificationEnvironmentFixture fixture)
    {
        _s3Client = fixture.S3Client;
        _sqsClient = fixture.SqsClient;
        _bucketName = fixture.BucketName;
        _sqsQueueUrl = fixture.SqsQueueUrl;
    }

    [Fact]
    public async Task TestS3EventLambdaFunction()
    {
        var key = $"text_{Guid.NewGuid()}.txt";

        
        
        // Create a bucket an object to setup a test data.
        await _s3Client.PutObjectAsync(new PutObjectRequest
        {
            BucketName = _bucketName,
            Key = key,
            ContentBody = "sample data"
        });

        var expectedMessage = new S3NotificationMessage(_bucketName, key, "ObjectCreated:Put");
        
        // To avoid accidentally receiving messages from a different run ask for specific message
        // IIdeally make sure that each run only use a dedicated infrastrcuture that is deployed before that run
        await _sqsClient.AssertMessageQueued(_sqsQueueUrl, expectedMessage);
    }
}