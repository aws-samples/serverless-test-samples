using System.Net;
using System.Text.Json;
using Amazon.Lambda.APIGatewayEvents;
using Amazon.Lambda.Core;
using AWS.Lambda.Powertools.Logging;
using AWS.Lambda.Powertools.Metrics;
using AWS.Lambda.Powertools.Tracing;
using ChatbotDemo.Infrastructure;

namespace ChatbotDemo.App.Handlers;

/// <summary>
/// This class abstracts the AWS interaction between Amazon API Gateway & AWS Lambda Function.
/// </summary>
/// <typeparam name="TInput">A generic request model</typeparam>
/// <typeparam name="TOutput">A generic output model</typeparam>
public abstract class ApiGatewayRequestHandler<TInput, TOutput>
{
    protected abstract HttpMethod Method { get; }
    protected abstract RequestType RequestType { get; }
    protected string ConnectionId { get; set; }
    protected readonly IServiceProvider ServiceProvider;

    protected ApiGatewayRequestHandler() : this(Startup.ServiceProvider)
    {
    }

    private ApiGatewayRequestHandler(IServiceProvider serviceProvider)
    {
        ServiceProvider = serviceProvider;
    }

    /// <summary>
    /// This method is used to perform any validation on the incoming records.
    /// </summary>
    /// <param name="request"></param>
    /// <returns></returns>
    protected abstract Task<bool> Validate(TInput request);

    /// <summary>
    /// This method is completely abstracted from AWS Infrastructure and is called for every request.
    /// </summary>
    /// <param name="request">Request Object</param>
    /// <param name="lambdaContext">Lambda Context</param>
    /// <returns>TOutput</returns>
    protected abstract Task<TOutput> Process(TInput request, ILambdaContext lambdaContext);


    /// <summary>
    /// This method is called for every Lambda invocation. This method takes in an API Gateway request event object and creates
    /// an event adapter for processing the request.
    /// </summary>
    /// <param name="request">Request Event received by the function handler</param>
    /// <param name="lambdaContext">Lambda Context</param>
    /// <returns></returns>
    [Logging(LogEvent = true, ClearState = true)]
    [Metrics(Namespace = "ApiGatewayRequestHandler", CaptureColdStart = true)]
    [Tracing(Namespace = "ApiGatewayRequestHandler", SegmentName = "ApiGatewayRequestHandler", CaptureMode = TracingCaptureMode.Error)]
    public async Task<APIGatewayProxyResponse> Handler(
        APIGatewayProxyRequest request,
        ILambdaContext lambdaContext)
    {
        try
        {
            ConnectionId = request.RequestContext.ConnectionId;
            
            // var method = new HttpMethod(request.RequestContext.HttpMethod);
            //
            // if (!method.Equals(Method))
            // {
            //     throw new NotSupportedException(
            //         $"Method {method} not allowed! Only {Method} allowed for this endpoint");
            // }

            var input = RequestType switch
            {
                RequestType.Querystring => (TInput)request.QueryStringParameters,
                RequestType.Path => (TInput)request.PathParameters,
                RequestType.Body => JsonSerializer.Deserialize<TInput>(request.Body),
                RequestType.None => JsonSerializer.Deserialize<TInput>(JsonSerializer.Serialize(request)),
                _ => throw new ArgumentOutOfRangeException()
            };

            // These abstract methods is implemented by the concrete classes
            await Validate(input);
            var response = await Process(input, lambdaContext);
            return await BuildSuccessfulResponse(request, response);
        }
        catch (Exception ex)
        {
            Logger.LogError(ex);
            return await BuildFailureResponse(request, lambdaContext, ex);
        }
    }

    /// <summary>
    /// This method builds a successful APIGatewayProxyResponse
    /// </summary>
    /// <param name="request"></param>
    /// <param name="result"></param>
    /// <returns></returns>
    private static Task<APIGatewayProxyResponse> BuildSuccessfulResponse(APIGatewayProxyRequest request, TOutput result)
    {
        var response = new APIGatewayProxyResponse
        {
            Headers = new Dictionary<string, string>
            {
                { "Content-Type", "application/json" },
                {
                    "Access-Control-Allow-Origin",
                    request.Headers.TryGetValue("origin", out var header) ? header : "*"
                },
                { "Access-Control-Allow-Credentials", "true" }
            },
            StatusCode = (int)HttpStatusCode.OK,
            Body = JsonSerializer.Serialize(result)
        };

        return Task.FromResult(response);
    }

    /// <summary>
    /// This method builds a APIGatewayProxyResponse when an exception occurs
    /// </summary>
    /// <param name="request"></param>
    /// <param name="lambdaContext"></param>
    /// <param name="exception"></param>
    /// <returns></returns>
    private Task<APIGatewayProxyResponse> BuildFailureResponse(APIGatewayProxyRequest request,
        ILambdaContext lambdaContext,
        Exception exception)
    {
        var response = new APIGatewayProxyResponse
        {
            Headers = new Dictionary<string, string>
            {
                { "Content-Type", "application/json" },
                {
                    "Access-Control-Allow-Origin",
                    request.Headers.TryGetValue("origin", out var header) ? header : "*"
                },
                { "Access-Control-Allow-Credentials", "true" },
                { "X-Amzn-ErrorType", exception.GetType().Name }
            },
            StatusCode = (int)HttpStatusCode.InternalServerError,
            Body = JsonSerializer.Serialize(new
                {
                    errorType = exception.GetType().Name,
                    httpStatus = (int)HttpStatusCode.InternalServerError,
                    errorMessage = exception.Message,
                    requestId = lambdaContext.AwsRequestId,
                    trace = exception.StackTrace,
                }
            )
        };
        return Task.FromResult(response);
    }
}