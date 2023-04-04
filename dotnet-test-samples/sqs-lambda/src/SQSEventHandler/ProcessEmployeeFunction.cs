using System;
using System.Threading.Tasks;
using Amazon.Lambda.Core;
using SqsEventHandler.Models;
using SqsEventHandler.Triggers;

// Assembly attribute to enable the Lambda function's JSON input to be converted into a .NET class.
[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace SqsEventHandler;

/// <summary>
/// This class implements the business logic of the function. The function handler can be found in
/// the base abstract class SqsEventTrigger::Handler
/// </summary>
public class ProcessEmployeeFunction : SqsEventTrigger<Employee>
{
    public override async Task ProcessSqsMessage(Employee message, ILambdaContext lambdaContext)
    {
        if (message == null)
            throw new ArgumentNullException(nameof(message));

        lambdaContext.Logger.LogLine($"Message: {message}");
        await Task.CompletedTask;
    }
}