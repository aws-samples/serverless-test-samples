using System.Text;
using System.Text.Json;
using Amazon.ApiGatewayManagementApi;
using Amazon.ApiGatewayManagementApi.Model;
using Amazon.Lambda.Core;
using Amazon.Lambda.SQSEvents;
using ChatbotDemo.App.Handlers;
using ChatbotDemo.Repositories;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Options;

namespace ChatbotDemo.App.Functions;

public class WsMessageFunction : SqsEventHandler<object>
{
    private readonly ApplicationConfigurationOptions _applicationConfigurationOptions;
    private Func<string, IAmazonApiGatewayManagementApi> ApiGatewayManagementApiClientFactory { get; }


    public WsMessageFunction()
    {
        _applicationConfigurationOptions =
            ServiceProvider.GetRequiredService<IOptions<ApplicationConfigurationOptions>>().Value;
        ApiGatewayManagementApiClientFactory = (Func<string, AmazonApiGatewayManagementApiClient>)((endpoint) =>
            new AmazonApiGatewayManagementApiClient(new AmazonApiGatewayManagementApiConfig
            {
                ServiceURL = endpoint
            }));
    }

    public override async Task ProcessSqsMessage(SQSEvent.SQSMessage sqsMessage, ILambdaContext lambdaContext)
    {
        var apiClient = ApiGatewayManagementApiClientFactory(_applicationConfigurationOptions.WebsocketCallbackUrl);
        if (sqsMessage.MessageAttributes.TryGetValue("connectionId", out var connectionId))
        {
            await apiClient.PostToConnectionAsync(new PostToConnectionRequest
            {
                ConnectionId = connectionId.StringValue,
                Data = new MemoryStream(Encoding.UTF8.GetBytes(JsonSerializer.Serialize("Leslie Daniel Raj")))
            });
        }
        else
            throw new ArgumentException($"Unable to find SQS message attribute: connectionId");
    }
}