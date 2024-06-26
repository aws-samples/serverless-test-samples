using Amazon.Lambda.Core;
using AWS.Lambda.Powertools.Logging;
using AWS.Lambda.Powertools.Metrics;
using AWS.Lambda.Powertools.Tracing;
using ChatbotDemo.Infrastructure;
using ChatbotDemo.Infrastructure.Models.Request;
using ChatbotDemo.Infrastructure.Models.Response;

namespace ChatbotDemo.App.Handlers;

/// <summary>
/// This class abstracts the interaction between Amazon Bedrock Action groups & AWS Lambda Function.
/// </summary>
/// <typeparam name="TRequest">An Amazon Bedrock action group request</typeparam>
/// <typeparam name="TResponse">An Amazon Bedrock action group response</typeparam>
public abstract class BedrockEventHandler<TRequest, TResponse> 
    where TRequest : class, IBedrockRequest
    where TResponse : class, IBedrockResponse, new()

{
    protected readonly IServiceProvider ServiceProvider;
    private TResponse _response;

    protected BedrockEventHandler() : this(Startup.ServiceProvider)
    {
    }

    private BedrockEventHandler(IServiceProvider serviceProvider)
    {
        ServiceProvider = serviceProvider;
        _response = new TResponse();
    }

    /// <summary>
    /// This method is completely abstracted from AWS Infrastructure and is called for every request.
    /// </summary>
    /// <param name="request">Bedrock Event Object</param>
    /// <param name="lambdaContext">Lambda Context</param>
    /// <returns></returns>
    public abstract Task<TResponse> ProcessBedrockEvent(TRequest request, ILambdaContext lambdaContext);

    /// <summary>
    /// This method is used to perform any validation on the incoming records.
    /// </summary>
    /// <param name="request"></param>
    /// <returns></returns>
    public abstract Task<bool> ValidateBedrockEvent(TRequest request);
    
    /// <summary>
    /// This method is used to perform any error handling scenarios.
    /// </summary>
    /// <param name="request"></param>
    /// <param name="response"></param>
    /// <returns></returns>
    protected abstract Task<TResponse> HandleErrors(TRequest request, TResponse response);

    /// <summary>
    /// This method is called for every Lambda invocation. This method takes in a Bedrock event object and creates
    /// a Bedrock Event adapter for processing the request.
    /// </summary>
    /// <param name="request">Bedrock Action Group Event received by the function handler</param>
    /// <param name="lambdaContext">Lambda Context</param>
    /// <returns></returns>
    [Logging(LogEvent = true, ClearState = true)]
    [Metrics(Namespace = "BedrockEventHandler", CaptureColdStart = true)]
    [Tracing(Namespace = "BedrockEventHandler", SegmentName = "BedrockEventHandler")]
    public async Task<TResponse> Handler(TRequest request, ILambdaContext lambdaContext)
    {
        await Process(request, lambdaContext);
        
        Logger.LogInformation(_response);
        return _response;
    }

    /// <summary>
    /// This method abstracts the Bedrock Event for downstream processing.
    /// </summary>
    /// <param name="request">Bedrock Event received by the function handler</param>
    /// <param name="lambdaContext">Lambda Context</param>
    [Tracing(SegmentName = "Process")]
    private async Task Process(TRequest request, ILambdaContext lambdaContext)
    {
        try
        {
            await ValidateBedrockEvent(request);
            _response = await ProcessBedrockEvent(request, lambdaContext);
            
            // Set Context in Response
            _response.MessageVersion = request.MessageVersion;
            _response.SessionAttributes = request.SessionAttributes;
            _response.PromptSessionAttribute = request.PromptSessionAttribute;
        }
        catch (Exception ex)
        {
            Logger.LogError(ex);
            
            _response = await HandleErrors(request, _response);
        }
    }
}