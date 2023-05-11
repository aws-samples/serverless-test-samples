namespace CreateCustomerFunction;

using Amazon.XRay.Recorder.Handlers.AwsSdk;

using AWS.Lambda.Powertools.Logging;
using AWS.Lambda.Powertools.Tracing;

using SchemaTesting.Shared;

using System.Text.Json;
using Amazon.EventBridge;
using Amazon.Lambda.APIGatewayEvents;

public class Function
{
    private readonly CreateCustomerCommandHandler _commandHandler;
    
    public Function() : this(null)
    {
    }

    internal Function(IEventPublisher? publisher)
    {
        AWSSDKHandler.RegisterXRayForAllServices();
        
        var eventPublisher = publisher ?? new EventBridgeEventPublisher(new AmazonEventBridgeClient());

        _commandHandler =
            new CreateCustomerCommandHandler(options => { options.EventVersionToPublish = EventVersion.V1; },
                eventPublisher);
    }

    [Logging(LogEvent = true)]
    [Tracing]
    public async Task<APIGatewayProxyResponse> FunctionHandler(APIGatewayProxyRequest apiGatewayProxyRequest)
    {
        var command = JsonSerializer.Deserialize<CreateCustomerCommand>(apiGatewayProxyRequest.Body);

        if (command == null)
        {
            return new APIGatewayProxyResponse()
            {
                StatusCode = 400
            };
        }

        var result = await this._commandHandler.Handle(command);

        return new APIGatewayProxyResponse()
        {
            StatusCode = result ? 201 : 400
        };
    }
}