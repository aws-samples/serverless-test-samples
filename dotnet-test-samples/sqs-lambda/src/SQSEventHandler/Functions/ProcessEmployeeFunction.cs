using System;
using System.Threading.Tasks;
using Amazon.Lambda.Core;
using AWS.Lambda.Powertools.Logging;
using AWS.Lambda.Powertools.Tracing;
using Microsoft.Extensions.DependencyInjection;
using SqsEventHandler.Handlers;
using SqsEventHandler.Infrastructure;
using SqsEventHandler.Models;
using SqsEventHandler.Repositories;
using SqsEventHandler.Repositories.Models;

// Assembly attribute to enable the Lambda function's JSON input to be converted into a .NET class.
[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace SqsEventHandler.Functions;

/// <summary>
/// This class implements the business logic of the function. The function handler can be found in
/// the base abstract class SqsEventHandler::Handler
/// </summary>
public class ProcessEmployeeFunction : SqsEventHandler<Employee>
{
    private readonly IDynamoDbRepository<EmployeeDto> _employeeRepository;

    public ProcessEmployeeFunction()
    {
        _employeeRepository = ServiceProvider.GetRequiredService<IDynamoDbRepository<EmployeeDto>>();
    }

    public ProcessEmployeeFunction(IDynamoDbRepository<EmployeeDto> employeeRepository)
    {
        _employeeRepository = employeeRepository;
    }

    [Tracing(SegmentName = "ProcessEmployeeFunction")]
    public override async Task ProcessSqsMessage(Employee message, ILambdaContext lambdaContext)
    {
        if (message == null)
            throw new ArgumentNullException(nameof(message));
        if (message.EmployeeId == null)
            throw new ArgumentNullException(nameof(message.EmployeeId));

        using var cts = lambdaContext.GetCancellationTokenSource();

        var response = await _employeeRepository.PutItemAsync(message.AsDto(), cts.Token);

        Logger.LogInformation($"{response}, {message}");
        await Task.CompletedTask;
    }
}