using System;
using System.ComponentModel.DataAnnotations;
using System.Net.Http;
using System.Threading.Tasks;
using Amazon.Lambda.Core;
using AWS.Lambda.Powertools.Logging;
using AWS.Lambda.Powertools.Tracing;
using ExampleApi.Handlers;
using Microsoft.Extensions.DependencyInjection;
using ExampleApi.Infrastructure;
using ExampleApi.Infrastructure.Models;
using ExampleApi.Models;
using ExampleApi.Repositories.Sql;

namespace ExampleApi.Functions;

/// <summary>
/// This class implements the business logic of the function. The function handler can be found in
/// the base abstract class ExampleApi::Handler
/// </summary>
public class PutEmployee : ApiGatewayRequestHandler<PutEmployeeRequest, PutEmployeeResponse>
{
    private readonly IEmployeeRepository _employeeRepository;

    public PutEmployee()
    {
        _employeeRepository = ServiceProvider.GetRequiredService<IEmployeeRepository>();
    }

    public PutEmployee(IEmployeeRepository employeeRepository)
    {
        _employeeRepository = employeeRepository;
    }

    protected override HttpMethod Method => HttpMethod.Put;
    protected override RequestType RequestType => RequestType.Body;

    [Tracing(SegmentName = "Validate")]
    protected override Task<bool> Validate(PutEmployeeRequest request)
    {
        Logger.LogWarning(request);
        
        if (request == null)
            throw new ArgumentNullException(nameof(request));
        if (request.Employee == null)
            throw new ArgumentNullException(nameof(request.Employee));
        
        if (string.IsNullOrWhiteSpace(request.Employee.EmployeeId))
            throw new ValidationException($"Invalid '{nameof(request.Employee.EmployeeId)}'.");

        return Task.FromResult(true);
    }

    [Tracing(SegmentName = "Process")]
    protected override async Task<PutEmployeeResponse> Process(PutEmployeeRequest request, ILambdaContext lambdaContext)
    {
        using var cts = lambdaContext.GetCancellationTokenSource();

        if (string.IsNullOrEmpty(request.Employee.EmployeeId))
            request.Employee.EmployeeId = Guid.NewGuid().ToString();
        
        var upsertResult = await _employeeRepository.PutEmployee(request.Employee.AsDto(), cts.Token);

        return new PutEmployeeResponse
        {
            EmployeeId = request.Employee.EmployeeId,
            Result = upsertResult
        };
    }
}