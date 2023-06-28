using System.Net.Http;
using System.Threading.Tasks;
using Amazon.Lambda.Core;
using AWS.Lambda.Powertools.Tracing;
using ExampleApi.Infrastructure;
using ExampleApi.Infrastructure.Models;
using ExampleApi.Handlers;
using ExampleApi.Models;

namespace ExampleApi.Functions;

/// <summary>
/// This class implements the business logic of the function. The function handler can be found in
/// the base abstract class ExampleApi::Handler
/// </summary>
public class GetHealth : ApiGatewayRequestHandler<GetHealthRequest, GetHealthResponse>
{
    public GetHealth()
    {
    }

    protected override HttpMethod Method => HttpMethod.Get;
    protected override RequestType RequestType => RequestType.None;

    [Tracing(SegmentName = "Validate")]
    protected override Task<bool> Validate(GetHealthRequest request)
    {
        return Task.FromResult(true);
    }

    [Tracing(SegmentName = "Process")]
    protected override Task<GetHealthResponse> Process(GetHealthRequest request,
        ILambdaContext lambdaContext)
    {
        using var cts = lambdaContext.GetCancellationTokenSource();

        return Task.FromResult(new GetHealthResponse
        {
            AwsRequestId = lambdaContext.AwsRequestId,
            FunctionName = lambdaContext.FunctionName,
            FunctionVersion = lambdaContext.FunctionVersion,
        });
    }
}