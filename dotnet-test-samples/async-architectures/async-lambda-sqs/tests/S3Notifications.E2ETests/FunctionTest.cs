using System.Text.Json;
using Amazon.S3;
using Amazon.S3.Model;
using S3Notifications.integrationTests.Fixtures;
using Xunit;

namespace S3Notifications.E2ETests;

public class FunctionTest : 
    IClassFixture<S3NotificationEnvironmentFixture>
{
    private readonly S3NotificationEnvironmentFixture _fixture;
    private readonly IAmazonS3 _s3Client;
    private readonly string _bucketName;

    public FunctionTest(S3NotificationEnvironmentFixture fixture)
    {
        _fixture = fixture;
        _s3Client = fixture.S3Client;
        _bucketName = fixture.BucketName;
    }

    [Fact]
    public async Task TestS3EventLambdaFunction()
    {
        var key = $"text_{Guid.NewGuid()}.txt";

        // Create a bucket an object to setup a test data.
        await _s3Client.PutBucketAsync(_bucketName);
        await _s3Client.PutObjectAsync(new PutObjectRequest
        {
            BucketName = _bucketName,
            Key = key,
            ContentBody = "sample data"
        });

        var message = await _fixture.GetNextMessage();
        var result = JsonSerializer.Deserialize<S3NotificationMessage>(message.Body);

        var expected = new S3NotificationMessage(_bucketName, key, "ObjectCreated:Put");
        
        Assert.Equal(expected, result);
    }
}