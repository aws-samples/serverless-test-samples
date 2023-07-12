using System.Net;
using System.Text.Json;
using Amazon.Lambda.S3Events;
using Amazon.Lambda.TestUtilities;
using Amazon.SQS;
using Amazon.SQS.Model;
using FakeItEasy;
using S3Notificatrions.TestUtilities.Builders;

namespace S3Notifications.UnitTests
{
    public class FunctionTest
    {
        [Fact]
        public async Task FunctionHandler_With_EmptyEvent_Should_ReturnNull()
        {
            var fakeSqsClient = A.Fake<IAmazonSQS>();
            var function = new Function(fakeSqsClient);

            var s3Event = new S3Event();

            var result = await function.FunctionHandler(s3Event, new TestLambdaContext());

            Assert.Null(result);
        }

        [Fact]
        public async Task FunctionHandler_With_EventWithoutAnyRecords_Should_ReturnNull()
        {
            var fakeSqsClient = A.Fake<IAmazonSQS>();
            var function = new Function(fakeSqsClient);

            var s3Event = new S3Event
            {
                Records = new List<S3Event.S3EventNotificationRecord>()
            };

            var result = await function.FunctionHandler(s3Event, new TestLambdaContext());

            Assert.Null(result);
        }

        [Fact]
        public async Task FunctionHandler_With_QueueNameNotSet_Should_ThrowException()
        {
            var fakeSqsClient = A.Fake<IAmazonSQS>();
            var function = new Function(fakeSqsClient);

            var s3Event = new S3Event
            {
                Records = new[]{
                    new S3EventNotificationRecordBuilder().Build()
                }.ToList()
            };

            Environment.SetEnvironmentVariable("QUEUE_URL", null);

            var exc = await Assert.ThrowsAsync<ApplicationException>(
                async () => await function.FunctionHandler(s3Event, new TestLambdaContext()));

            Assert.Equal("QUEUE_URL was not set", exc.Message);
        }

        [Fact]
        public async Task FunctionHandler_With_QueueNameSet_Should_QueueNewMessage()
        {
            var fakeSqsClient = A.Fake<IAmazonSQS>();
            var function = new Function(fakeSqsClient);

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

            Environment.SetEnvironmentVariable("QUEUE_URL", "http://queue");

            SendMessageRequest jsonResult = null;
            A.CallTo(() => fakeSqsClient.SendMessageAsync(A<SendMessageRequest>._, A<CancellationToken>._))
                .Invokes(call =>
                {
                    jsonResult = call.Arguments.Get<SendMessageRequest>(0);
                })
                .Returns(Task.FromResult(new SendMessageResponse
                {
                    HttpStatusCode = HttpStatusCode.OK,
                    MessageId = "1234"
                }));

            await function.FunctionHandler(s3Event, new TestLambdaContext());

            var result = JsonSerializer.Deserialize<S3NotificationMessage>(jsonResult.MessageBody);
            var expected = new S3NotificationMessage("bucket-name", "key-1", "event-name");

            Assert.Equal(expected, result);
        }

        [Fact]
        public async Task FunctionHandler_With_QueueNameSet_Should_ReturnMessageId()
        {
            var fakeSqsClient = A.Fake<IAmazonSQS>();
            var function = new Function(fakeSqsClient);

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

            Environment.SetEnvironmentVariable("QUEUE_url", "http://queue");

            A.CallTo(() => fakeSqsClient.SendMessageAsync(A<SendMessageRequest>._, A<CancellationToken>._))
                .Returns(Task.FromResult(new SendMessageResponse
                {
                    HttpStatusCode = HttpStatusCode.OK,
                    MessageId = "1234"
                }));

            var result = await function.FunctionHandler(s3Event, new TestLambdaContext());

            Assert.Equal("1234", result);
        }
    }
}