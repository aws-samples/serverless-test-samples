using Amazon.Lambda.S3Events;
using S3Notifications.integrationTests.Fixtures;
using S3Notificatrions.TestUtilities.Builders;
using System.Text.Json;
using Amazon.Lambda.TestUtilities;

namespace S3Notifications.integrationTests;

public class FunctionTest : IClassFixture<SqsTestFixture>
{
    private readonly SqsTestFixture _fixture;

    public FunctionTest(SqsTestFixture fixture)
    {
        _fixture = fixture;
        Environment.SetEnvironmentVariable("QUEUE_URL", fixture.QueueUrl);
    }

    [Fact]
    public async Task FunctionHandler_With_QueueNameSet_Should_QueueNewMessage()
    {
        var function = new Function(_fixture.SqsClient);

        var s3Event = new S3Event
        {
            Records = new[]{
                new S3EventNotificationRecordBuilder()
                    .EventName("event-name")
                    .BucketName("bucket-name")
                    .ObjectKey("key-1")
                    .Build()
            }.ToList()
        };

        await function.FunctionHandler(s3Event, new TestLambdaContext());

        var message = await _fixture.GetNextMessage();
            
        var result = JsonSerializer.Deserialize<S3NotificationMessage>(message.Body);
        var expected = new S3NotificationMessage("bucket-name", "key-1", "event-name");

        Assert.Equal(expected, result);
    }
    
    [Fact]
    public async Task FunctionHandler_With_QueueNameSet_Should_ReturnMessageId()
    {
        var function = new Function(_fixture.SqsClient);

        var s3Event = new S3Event
        {
            Records = new[]{
                new S3EventNotificationRecordBuilder()
                    .EventName("event-name")
                    .BucketName("bucket-name")
                    .ObjectKey("key-1")
                    .Build()
            }.ToList()
        };

        var result = await function.FunctionHandler(s3Event, new TestLambdaContext());

        var message = await _fixture.GetNextMessage();
        
        Assert.Equal(message.MessageId, result);
    }
}