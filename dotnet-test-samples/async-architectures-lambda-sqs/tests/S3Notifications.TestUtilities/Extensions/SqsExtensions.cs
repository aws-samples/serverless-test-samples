using System.Text.Json;
using Amazon.SQS;
using Amazon.SQS.Model;
using Xunit;

namespace S3Notifications.TestUtilities.Extensions;

public static class SqsExtensions
{
    public static async Task<T> GetNextMessage<T>(this IAmazonSQS sqsClient, string sqsQueueUrl)
    {
        var message = await GetNextSqsMessage(sqsClient, sqsQueueUrl);

        return JsonSerializer.Deserialize<T>(message.Body)!;
    }

    public static async Task<Message> GetNextSqsMessage(this IAmazonSQS sqsClient, string sqsQueueUrl)
    {
        var receiveMessageResponse = await GetNextMessageInternal(sqsClient, sqsQueueUrl);

        Assert.NotNull(receiveMessageResponse);
        Assert.NotEmpty(receiveMessageResponse.Messages);

        var message = receiveMessageResponse.Messages[0];
        await sqsClient.DeleteMessageAsync(sqsQueueUrl, message.ReceiptHandle);

        Assert.NotNull(message.Body);
        return message;
    }

    private static async Task<ReceiveMessageResponse> GetNextMessageInternal(IAmazonSQS sqsClient, string sqsQueueUrl)
    {
        return await GetNextMessageInternal(sqsClient, sqsQueueUrl, _ => true);
    }
    private static async Task<ReceiveMessageResponse> GetNextMessageInternal(IAmazonSQS sqsClient, string sqsQueueUrl, Predicate<Message> checkForMessage)
    {
        var receiveMessageRequest = new ReceiveMessageRequest
        {
            QueueUrl = sqsQueueUrl,

            // Handle massages one by one
            MaxNumberOfMessages = 1,

            // make sure messages are handled even if run by concurrent test
            VisibilityTimeout = 1,

            // use long polling to improve response time
            WaitTimeSeconds = 20
        };

        var count = 0;
        ReceiveMessageResponse? receiveMessageResponse;
        do
        {
            receiveMessageResponse = await sqsClient.ReceiveMessageAsync(receiveMessageRequest);
            if (receiveMessageResponse.Messages.Count != 0 && 
                checkForMessage.Invoke(receiveMessageResponse.Messages[0]))
            {
                break;
            }
        } while (count++ < 30); // 20 secs * 30 = 10 min max

        return receiveMessageResponse;
    }

    public static async Task AssertMessageQueued<T>(this IAmazonSQS sqsClient, string sqsQueueUrl, T expected)
    {
        var expectedJson = JsonSerializer.Serialize(expected);
        
        var response = await GetNextMessageInternal(
            sqsClient, sqsQueueUrl,
            message => message.Body.Equals(expectedJson));
        
        Assert.NotNull(response);
    }
}