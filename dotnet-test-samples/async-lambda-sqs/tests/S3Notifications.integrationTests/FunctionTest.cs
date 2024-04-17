using Amazon.Lambda.S3Events;
using S3Notifications.integrationTests.Fixtures;
using S3Notificatrions.TestUtilities.Builders;
using System.Text.Json;
using Amazon.Lambda.TestUtilities;
using Amazon.SQS;
using S3Notifications.TestUtilities.Extensions;

namespace S3Notifications.integrationTests;

public class FunctionTest : IClassFixture<SqsTestFixture>
{
    private readonly IAmazonSQS _sqsClient;
    private readonly string _fixtureQueueUrl;

    public FunctionTest(SqsTestFixture fixture)
    {
        _sqsClient = fixture.SqsClient;
        _fixtureQueueUrl = fixture.QueueUrl;
        Environment.SetEnvironmentVariable("QUEUE_URL", _fixtureQueueUrl);
    }

    [Fact]
    public async Task FunctionHandler_With_QueueNameSet_Should_QueueNewMessage()
    {
        var function = new Function(_sqsClient);

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

        var result = await _sqsClient.GetNextMessage<S3NotificationMessage>(_fixtureQueueUrl);
            
        var expected = new S3NotificationMessage("bucket-name", "key-1", "event-name");

        Assert.Equal(expected, result);
    }
    
    [Fact]
    public async Task FunctionHandler_With_QueueNameSet_Should_ReturnMessageId()
    {
        var function = new Function(_sqsClient);

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

        var message = await _sqsClient.GetNextSqsMessage(_fixtureQueueUrl);
        
        Assert.Equal(message.MessageId, result);
    }
}