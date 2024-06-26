using Amazon.Lambda.Core;
using ChatbotDemo.App.Handlers;
using ChatbotDemo.Infrastructure;
using ChatbotDemo.Repositories;
using ChatbotDemo.Repositories.Mappers;
using ChatbotDemo.Repositories.Models;
using Microsoft.Extensions.DependencyInjection;
using HttpMethod = System.Net.Http.HttpMethod;

namespace ChatbotDemo.App.Functions;

public class WsOnConnectFunction : ApiGatewayRequestHandler<object, object>
{
    private readonly IDynamoDbRepository<ConnectionDto> _connectionRepository;

    public WsOnConnectFunction()
    {
        _connectionRepository = ServiceProvider.GetRequiredService<IDynamoDbRepository<ConnectionDto>>();
    }

    protected override HttpMethod Method => null;
    protected override RequestType RequestType => RequestType.None;

    protected override Task<bool> Validate(object request)
    {
        return Task.FromResult(true);
    }

    protected override async Task<object> Process(object request, ILambdaContext lambdaContext)
    {
        using var cts = lambdaContext.GetCancellationTokenSource();


        var result = await _connectionRepository.PutItemAsync(
            new Models.Connection
            {
                ConnectionId = ConnectionId
            }.AsDto(),
            cts.Token
        );

        return new
        {
            ConnectionId,
            Result = result is UpsertResult.Inserted or UpsertResult.Updated
                ? "Connected"
                : "Failed"
        };
    }
}