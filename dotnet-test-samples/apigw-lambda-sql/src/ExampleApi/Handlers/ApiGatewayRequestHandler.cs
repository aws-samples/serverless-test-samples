using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;
using Amazon.Lambda.APIGatewayEvents;
using Amazon.Lambda.Core;
using AWS.Lambda.Powertools.Logging;
using AWS.Lambda.Powertools.Metrics;
using AWS.Lambda.Powertools.Tracing;
using ExampleApi.Infrastructure;
using ExampleApi.Infrastructure.Models;

// Assembly attribute to enable the Lambda function's JSON request to be converted into a .NET class.
[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace ExampleApi.Handlers;

/// <summary>
/// This class abstracts the AWS interaction between Amazon API Gateway & AWS Lambda Function.
/// </summary>
/// <typeparam name="TInput">A generic request model</typeparam>
/// <typeparam name="TOutput">A generic output model</typeparam>
public abstract class ApiGatewayRequestHandler<TInput, TOutput>
{
    protected abstract HttpMethod Method { get; }
    protected abstract RequestType RequestType { get; }
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
    /// <param name="request">Kinesis Record Object</param>
    /// <param name="lambdaContext">Lambda Context</param>
    /// <returns>TOutput</returns>
    protected abstract Task<TOutput> Process(TInput request, ILambdaContext lambdaContext);


    /// <summary>
    /// This method is called for every Lambda invocation. This method takes in a Kinesis event object and creates
    /// an Kinesis Event adapter for processing the shard of Kinesis records.
    /// </summary>
    /// <param name="request">Kinesis Event received by the function handler</param>
    /// <param name="lambdaContext">Lambda Context</param>
    /// <returns></returns>
    [Logging(LogEvent = true, ClearState = true)]
    [Metrics(Namespace = "ExampleApi", CaptureColdStart = true)]
    [Tracing(Namespace = "ExampleApi", SegmentName = "ExampleApi", CaptureMode = TracingCaptureMode.ResponseAndError)]
    public async Task<APIGatewayProxyResponse> Handler(
        APIGatewayProxyRequest request,
        ILambdaContext lambdaContext)
    {
        try
        {
            var method = new HttpMethod(request.RequestContext.HttpMethod);

            if (!method.Equals(Method))
            {
                throw new NotSupportedException(
                    $"Method {method} not allowed! Only {Method} allowed for this endpoint");
            }

            var input = RequestType switch
            {
                RequestType.None => default,
                RequestType.Querystring => DeserializeParameters(request.QueryStringParameters),
                RequestType.Path => DeserializeParameters(request.PathParameters),
                RequestType.Body => JsonSerializer.Deserialize<TInput>(request.Body),
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
            return await BuildFailureResponse(request, ex);
        }
    }

    /// <summary>
    /// This method deserializes the querystring or path parameters that are fed in as Dictionary.
    /// </summary>
    /// <param name="parameters"></param>
    /// <returns>Deserialized TInput object</returns>
    private static TInput DeserializeParameters(IDictionary<string, string> parameters)
    {
        var json = JsonSerializer.Serialize(parameters);
        return JsonSerializer.Deserialize<TInput>(json);
    }

    /// <summary>
    /// This method builds a successful APIGatewayProxyResponse
    /// </summary>
    /// <param name="request"></param>
    /// <param name="result"></param>
    /// <returns></returns>
    private Task<APIGatewayProxyResponse> BuildSuccessfulResponse(APIGatewayProxyRequest request, TOutput result)
    {
        var response = new APIGatewayProxyResponse
        {
            Headers = new Dictionary<string, string>
            {
                { "Content-Type", "application/json" },
                {
                    "Access-Control-Allow-Origin", request.Headers.ContainsKey("origin")
                        ? request.Headers["origin"]
                        : "*"
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
    /// <param name="exception"></param>
    /// <returns></returns>
    private Task<APIGatewayProxyResponse> BuildFailureResponse(APIGatewayProxyRequest request,
        Exception exception)
    {
        var response = new APIGatewayProxyResponse
        {
            Headers = new Dictionary<string, string>
            {
                { "Content-Type", "application/json" },
                {
                    "Access-Control-Allow-Origin",
                    request.Headers.ContainsKey("origin") ? request.Headers["origin"] : "*"
                },
                { "Access-Control-Allow-Credentials", "true" },
                { "X-Amzn-ErrorType", exception.GetType().Name }
            },
            StatusCode = (int)HttpStatusCode.InternalServerError,
            Body = JsonSerializer.Serialize(new
                {
                    errorType = exception.GetType().Name,
                    httpStatus = (int)HttpStatusCode.InternalServerError,
                    errorMessage = exception.Message
                }
            )
        };
        return Task.FromResult(response);
    }
}