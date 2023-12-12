namespace CreateCustomerFunction;

using Amazon.XRay.Recorder.Handlers.AwsSdk;

using AWS.Lambda.Powertools.Logging;
using AWS.Lambda.Powertools.Tracing;

using SchemaTesting.Shared;

using System.Text.Json;
using Amazon.EventBridge;
using Amazon.Lambda.Annotations;
using Amazon.Lambda.Annotations.APIGateway;
using Amazon.Lambda.APIGatewayEvents;

public class Function
{
    private readonly CreateCustomerCommandHandler _commandHandler;
    
    public Function(CreateCustomerCommandHandler commandHandler)
    {
        this._commandHandler = commandHandler;
    }

    [Logging(LogEvent = true)]
    [Tracing]
    [LambdaFunction]
    [RestApi(LambdaHttpMethod.Post, "/customer")]
    public async Task<IHttpResult> FunctionHandler([FromBody] CreateCustomerCommand command)
    {
        var result = await this._commandHandler.Handle(command);

        return result.Success ? HttpResults.Ok("OK") : HttpResults.BadRequest(result);
    }
}