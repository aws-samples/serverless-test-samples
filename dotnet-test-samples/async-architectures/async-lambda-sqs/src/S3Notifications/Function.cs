using System.Text.Json;
using Amazon.Lambda.Core;
using Amazon.Lambda.S3Events;
using Amazon.SQS;
using Amazon.SQS.Model;

// Assembly attribute to enable the Lambda function's JSON input to be converted into a .NET class.
[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace S3Notifications;

public class Function
{
    private const string QueueNameEnvKey = "QUEUE_NAME";
    private IAmazonSQS SqsClient { get; }

    /// <summary>
    /// Default constructor. This constructor is used by Lambda to construct the instance. When invoked in a Lambda environment
    /// the AWS credentials will come from the IAM role associated with the function and the AWS region will be set to the
    /// region the Lambda function is executed in.
    /// </summary>
    public Function()
    {
        SqsClient = new AmazonSQSClient();
    }

    /// <summary>
    /// Constructs an instance with a preconfigured SQS client. This can be used for testing the outside of the Lambda environment.
    /// </summary>
    
    public Function(IAmazonSQS sqsClient)
    {
        SqsClient = sqsClient;
    }

    /// <summary>
    /// This method is called for every Lambda invocation. This method takes in an S3 event object and can be used 
    /// to respond to S3 notifications.
    /// </summary>
    /// <param name="evnt"></param>
    /// <param name="context"></param>
    /// <returns></returns>
    public async Task<string?> FunctionHandler(S3Event evnt, ILambdaContext context)
    {
        if (evnt.Records?.Count is null or 0)
        {
            return null;
        }

        var s3Event = evnt.Records[0];

        var message = new S3NotificationMessage(s3Event.S3.Bucket.Name, s3Event.S3.Object.Key, s3Event.EventName);

        var queueName = Environment.GetEnvironmentVariable(QueueNameEnvKey);
        
        if (queueName == null)
        {
            throw new ApplicationException($"{QueueNameEnvKey} was not set");
        }

        return await SendMessageToQueue(queueName, message);
    }

    private async Task<string> SendMessageToQueue(string? queueName, S3NotificationMessage message)
    {
        var getQueueUrlResponse = await SqsClient.GetQueueUrlAsync(queueName);

        var jsonString = JsonSerializer.Serialize(message);

        var sendMessageRequest = new SendMessageRequest(getQueueUrlResponse.QueueUrl, jsonString);
        var sendMessageResponse = await SqsClient.SendMessageAsync(sendMessageRequest);

        return sendMessageResponse.MessageId;
    }
}