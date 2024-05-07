using Amazon.Lambda.Core;

// Assembly attribute to enable the Lambda function's JSON input to be converted into a .NET class.
[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace AsyncTesting.IntegrationTestListener;

using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.Model;
using Amazon.Lambda.Core;
using Amazon.Lambda.S3Events;
using Amazon.S3;
using Amazon.XRay.Recorder.Handlers.AwsSdk;

using AWS.Lambda.Powertools.Logging;
using AWS.Lambda.Powertools.Tracing;

public class Function
{
    private IAmazonS3 _s3Client;
    private IAmazonDynamoDB _dynamoDbClient;
    
    public Function() : this(null, null)
    {
        AWSSDKHandler.RegisterXRayForAllServices();
    }
    
    public Function(IAmazonS3? s3Client, IAmazonDynamoDB? dynamoDb)
    {
        this._s3Client = s3Client ?? new AmazonS3Client();
        this._dynamoDbClient = dynamoDb ?? new AmazonDynamoDBClient();
    }
    
    [Logging(LogEvent = true)]
    [Tracing]
    public async Task FunctionHandler(S3Event evt)
    {
        var eventRecords = evt.Records ?? new List<S3Event.S3EventNotificationRecord>();
        
        Logger.LogInformation($"Received {eventRecords.Count} record(s) from S3");

        foreach (var record in eventRecords)
        {
            await this.ProcessS3Record(record);
        }
    }

    [Tracing]
    private async Task ProcessS3Record(S3Event.S3EventNotificationRecord record)
    {
        var s3Event = record.S3;

        if (s3Event == null)
        {
            Logger.LogWarning("S3 Event object is null, skipping");
            return;
        }

        try
        {
            Logger.LogInformation($"Processing object {record.S3.Object.Key} from bucket {record.S3.Bucket.Name}");

            var originalObject = await this._s3Client.GetObjectAsync(
                record.S3.Bucket.Name,
                record.S3.Object.Key);

            // convert stream to string
            var reader = new StreamReader(originalObject.ResponseStream);

            var message = await reader.ReadToEndAsync();

            Logger.LogInformation($"Parsed event body is {message}");

            await this._dynamoDbClient.PutItemAsync(
                Environment.GetEnvironmentVariable("RESULTS_TABLE"),
                new Dictionary<string, AttributeValue>(2)
                {
                    { "id", new AttributeValue(record.S3.Object.Key) },
                    { "message", new AttributeValue(message) }
                });
        }
        catch (Exception e)
        {
            Logger.LogError(
                $"Error getting object {s3Event.Object.Key} from bucket {s3Event.Bucket.Name}. Make sure they exist and your bucket is in the same region as this function.",
                e);
            throw;
        }
    }
}