using System;
using System.Threading.Tasks;
using Amazon.Lambda.Core;
using Amazon.Lambda.SQSEvents;

// Assembly attribute to enable the Lambda function's JSON input to be converted into a .NET class.
[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace SQSEventHandler;

public class Function
{
    /// <summary>
    /// Default constructor. This constructor is used by Lambda to construct the instance. When invoked in a Lambda environment
    /// the AWS credentials will come from the IAM role associated with the function and the AWS region will be set to the
    /// region the Lambda function is executed in.
    /// </summary>
    public Function()
    {
    }

    /// <summary>
    /// This method is called for every Lambda invocation. This method takes in an SQS event object and can be used 
    /// to respond to SQS messages.
    /// </summary>
    /// <param name="sqsEvent"></param>
    /// <param name="context"></param>
    /// <returns></returns>
    public async Task SqsHandler(SQSEvent sqsEvent, ILambdaContext context)
    {
        if (sqsEvent != null)
        {
            context.Logger.LogLine($"Beginning to process {sqsEvent.Records.Count} records...");

            foreach (var sqsMessage in sqsEvent.Records)
            {
                context.Logger.LogLine($"Message Id: {sqsMessage.MessageId}");
                context.Logger.LogLine($"Event Source: {sqsMessage.EventSource}");
                context.Logger.LogLine($"Record Body: {sqsMessage.Body}");
            }
        }

        context.Logger.LogLine("Processing complete.");
        await Task.CompletedTask;
    }
}