using Amazon.Lambda.Core;
using ChatbotDemo.App.Handlers;
using ChatbotDemo.Infrastructure.Models.Request;
using ChatbotDemo.Infrastructure.Models.Response;

namespace ChatbotDemo.App.Functions;

public class
    ActionGroupFunction : BedrockEventHandler<BedrockFunctionDetailsRequest, BedrockFunctionDetailsResponse>
{
    public ActionGroupFunction()
    {
    }

    public override Task<BedrockFunctionDetailsResponse> ProcessBedrockEvent(BedrockFunctionDetailsRequest request,
        ILambdaContext lambdaContext)
    {
        var response = new BedrockFunctionDetailsResponse
        {
            Response = new FunctionDetailsResponseBuilder(request)
                .WithBody("Chicken has 20 gm of fat per serving. Shrimp has 30 gm of fat per serving. Beef has 50 gm of fat per serving")
        };

        return Task.FromResult(response);
    }

    public override Task<bool> ValidateBedrockEvent(BedrockFunctionDetailsRequest request)
    {
        return Task.FromResult(true);
    }

    protected override Task<BedrockFunctionDetailsResponse> HandleErrors(BedrockFunctionDetailsRequest request,
        BedrockFunctionDetailsResponse response)
    {
        response.Response = new FunctionDetailsResponseBuilder(request)
            .WithResponseState("FAILURE");

        return Task.FromResult(response);
    }
}