using System;
using System.Threading.Tasks;
using Amazon.Lambda.Core;
using AWS.Lambda.Powertools.Logging;
using AWS.Lambda.Powertools.Tracing;
using KinesisEventHandler.Handlers;
using KinesisEventHandler.Models;
using KinesisEventHandler.Repositories;
using KinesisEventHandler.Repositories.Models;
using Microsoft.Extensions.DependencyInjection;
using KinesisEventHandler.Infrastructure;

// Assembly attribute to enable the Lambda function's JSON input to be converted into a .NET class.
[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace KinesisEventHandler.Functions;

/// <summary>
/// This class implements the business logic of the function. The function handler can be found in
/// the base abstract class KinesisEventHandler::Handler
/// </summary>
public class ProcessEmployeeFunction : KinesisEventHandler<Employee>
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
    public override async Task ProcessKinesisRecord(Employee message, ILambdaContext lambdaContext)
    {
        if (message == null)
            throw new ArgumentNullException(nameof(message));
        if (message.EmployeeId == null)
            throw new ArgumentNullException(nameof(message.EmployeeId));

        using var cts = lambdaContext.GetCancellationTokenSource();

        var response = await _employeeRepository.PutItemAsync(message.AsDto(), cts.Token);

        Logger.LogInformation($"{response}, {message}");
    }
}