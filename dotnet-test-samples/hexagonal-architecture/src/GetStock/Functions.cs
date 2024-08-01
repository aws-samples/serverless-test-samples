using System.Net;
using System.Text.Json;
using Amazon.DynamoDBv2;
using Amazon.Lambda.APIGatewayEvents;
using Amazon.Lambda.Core;
using AWS.Lambda.Powertools.Logging;
using GetStock.Adapters;
using GetStock.Domains;
using GetStock.Ports;
using Microsoft.Extensions.DependencyInjection;

namespace GetStock;

public static class DI
{
    private static ServiceProvider? _serviceProvider;

    public static ServiceProvider ServiceProvider
    {
        get
        {
            if (_serviceProvider == null)
            {
                _serviceProvider = InitializeServiceProvider();
            }

            return _serviceProvider;
        }
    }

    private static ServiceProvider InitializeServiceProvider()
    {
        var services = new ServiceCollection();
        
        services.AddPortsServices();
        services.AddDomainServices();
        services.AddAdapters();
        
        services.AddSingleton<IAmazonDynamoDB, AmazonDynamoDBClient>();
        
        return services.BuildServiceProvider();
    }
}

public class Functions
{
    private readonly IHttpHandler _handler;

    public Functions()
    {
        _handler = DI.ServiceProvider.GetRequiredService<IHttpHandler>();
    }

    public Functions(IHttpHandler handler)
    {
        _handler = handler;
    }

    [Logging(LogEvent = true)]
    public APIGatewayProxyResponse GetStockById(APIGatewayProxyRequest request, ILambdaContext context)
    {
        var getValueResult = request.PathParameters.TryGetValue("StockId", out var stockId);
        if (!getValueResult || stockId == null)
        {
            return new APIGatewayProxyResponse
            {
                StatusCode = (int)HttpStatusCode.BadRequest,
                Body = "Status id not found on request"
            };
        }

        Logger.LogInformation($"StockId:{stockId}");

        var result = _handler.RetrieveStockValues(stockId).Result;

        Logger.LogInformation($"result:{result}");

        var response = new APIGatewayProxyResponse
        {
            StatusCode = (int)HttpStatusCode.OK,
            Body = JsonSerializer.Serialize(result),
            Headers = new Dictionary<string, string> { { "Content-Type", "text/json" } }
        };

        return response;
    }
}