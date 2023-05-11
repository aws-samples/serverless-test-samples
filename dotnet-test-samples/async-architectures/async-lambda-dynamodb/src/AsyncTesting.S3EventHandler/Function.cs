using Amazon.Lambda.Core;
using Amazon.Lambda.S3Events;
using Amazon.S3;
using Amazon.S3.Util;

// Assembly attribute to enable the Lambda function's JSON input to be converted into a .NET class.
[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace AsyncTesting.S3EventHandler;

using System.Text;

using Amazon.S3.Model;
using Amazon.XRay.Recorder.Handlers.AwsSdk;

using AWS.Lambda.Powertools.Logging;
using AWS.Lambda.Powertools.Tracing;

public class Function
{
    private IAmazonS3 _s3Client;

    /// <summary>
    /// Default constructor. This constructor is used by Lambda to construct the instance. When invoked in a Lambda environment
    /// the AWS credentials will come from the IAM role associated with the function and the AWS region will be set to the
    /// region the Lambda function is executed in.
    /// </summary>
    public Function() : this(null)
    {
        AWSSDKHandler.RegisterXRayForAllServices();
    }

    /// <summary>
    /// Constructs an instance with a preconfigured S3 client. This can be used for testing outside of the Lambda environment.
    /// </summary>
    /// <param name="s3Client"></param>
    public Function(IAmazonS3? s3Client)
    {
        this._s3Client = s3Client ?? new AmazonS3Client();
    }

    /// <summary>
    /// This method is called for every Lambda invocation. This method takes in an S3 event object and can be used 
    /// to respond to S3 notifications.
    /// </summary>
    /// <param name="evnt"></param>
    /// <param name="context"></param>
    /// <returns></returns>
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
            using var reader = new StreamReader(originalObject.ResponseStream);

            var lowerCaseMessage = await reader.ReadToEndAsync();

            Logger.LogInformation($"Parsed event body is {lowerCaseMessage}");

            var upperCaseMessage = lowerCaseMessage.ToUpper();

            var inputBytes = Encoding.ASCII.GetBytes(upperCaseMessage);

            Logger.LogInformation("Storing transformed data in S3");

            await this._s3Client.PutObjectAsync(
                new PutObjectRequest()
                {
                    BucketName = Environment.GetEnvironmentVariable("DESTINATION_BUCKET"),
                    InputStream = new MemoryStream(inputBytes),
                    Key = record.S3.Object.Key
                });
        }
        catch (Exception e)
        {
            Logger.LogError(
                $"Error getting object {s3Event.Object.Key} from bucket {s3Event.Bucket.Name}. Make sure they exist and your bucket is in the same region as this function.",
                e);
            
            // A DLQ is added to the Lambda function, re-throwing the exception here will route the message to the DLQ.
            throw;
        }
    }
}