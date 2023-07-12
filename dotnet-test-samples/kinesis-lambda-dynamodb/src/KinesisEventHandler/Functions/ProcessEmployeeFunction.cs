using System;
using System.ComponentModel.DataAnnotations;
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

    [Tracing(SegmentName = "ProcessKinesisRecord")]
    public override async Task ProcessKinesisRecord(Employee record, ILambdaContext lambdaContext)
    {
        using var cts = lambdaContext.GetCancellationTokenSource();
        var response = await _employeeRepository.PutItemAsync(record.AsDto(), cts.Token);
        Logger.LogInformation($"{response}, {record}");
    }

    [Tracing(SegmentName = "ValidateKinesisRecord")]
    public override Task<bool> ValidateKinesisRecord(Employee record)
    {
        if (record == null)
            throw new ArgumentNullException(nameof(record));
        if (string.IsNullOrEmpty(record.EmployeeId))
            throw new ValidationException($"'{nameof(record.EmployeeId)}' cannot be null or empty");

        return Task.FromResult(true);
    }
}