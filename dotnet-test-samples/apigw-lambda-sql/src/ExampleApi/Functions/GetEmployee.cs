using System.ComponentModel.DataAnnotations;
using System.Net.Http;
using System.Threading.Tasks;
using Amazon.Lambda.Core;
using AWS.Lambda.Powertools.Tracing;
using Microsoft.Extensions.DependencyInjection;
using ExampleApi.Infrastructure;
using ExampleApi.Infrastructure.Models;
using ExampleApi.Repositories.Sql;
using System;
using ExampleApi.Handlers;
using ExampleApi.Models;

namespace ExampleApi.Functions;

/// <summary>
/// This class implements the business logic of the function. The function handler can be found in
/// the base abstract class ExampleApi::Handler
/// </summary>
public class GetEmployee : ApiGatewayRequestHandler<GetEmployeeRequest, GetEmployeeResponse>
{
    private readonly IEmployeeRepository _employeeRepository;

    public GetEmployee()
    {
        _employeeRepository = ServiceProvider.GetRequiredService<IEmployeeRepository>();
    }

    public GetEmployee(IEmployeeRepository employeeRepository)
    {
        _employeeRepository = employeeRepository;
    }

    protected override HttpMethod Method => HttpMethod.Get;
    protected override RequestType RequestType => RequestType.Querystring;

    [Tracing(SegmentName = "Validate")]
    protected override Task<bool> Validate(GetEmployeeRequest request)
    {
        if (request == null)
            throw new ArgumentNullException(nameof(request));
        if (string.IsNullOrWhiteSpace(request.EmployeeId))
            throw new ValidationException($"Invalid '{nameof(request.EmployeeId)}'.");

        return Task.FromResult(true);
    }

    [Tracing(SegmentName = "Process")]
    protected override async Task<GetEmployeeResponse> Process(GetEmployeeRequest request,
        ILambdaContext lambdaContext)
    {
        using var cts = lambdaContext.GetCancellationTokenSource();
        var response = await _employeeRepository.GetEmployee(request.EmployeeId, cts.Token);

        return new GetEmployeeResponse
        {
            Employee = new Employee
            {
                EmployeeId = response.EmployeeId
            }
        };
    }
}