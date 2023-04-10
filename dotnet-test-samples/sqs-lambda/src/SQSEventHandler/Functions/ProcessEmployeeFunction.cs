using System;
using System.Threading.Tasks;
using Amazon.Lambda.Core;
using AWS.Lambda.Powertools.Logging;
using AWS.Lambda.Powertools.Tracing;
using SqsEventHandler.Handlers;
using SqsEventHandler.Models;

// Assembly attribute to enable the Lambda function's JSON input to be converted into a .NET class.
[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace SqsEventHandler.Functions;

/// <summary>
/// This class implements the business logic of the function. The function handler can be found in
/// the base abstract class SqsEventHandler::Handler
/// </summary>
public class ProcessEmployeeFunction : SqsEventHandler<Employee>
{
    [Tracing(SegmentName = "ProcessEmployeeFunction")]
    public override async Task ProcessSqsMessage(Employee message, ILambdaContext lambdaContext)
    {
        if (message == null)
            throw new ArgumentNullException(nameof(message));
        if (message.EmployeeId == null)
            throw new ArgumentNullException(nameof(message.EmployeeId));

        Logger.LogInformation($"Message: {message}");
        await Task.CompletedTask;
    }
}