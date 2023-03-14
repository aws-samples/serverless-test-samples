using System.Net;
using System.Reflection.Metadata;
using System.Text.Json;
using Amazon.DynamoDBv2;
using Amazon.Lambda.APIGatewayEvents;
using Amazon.Lambda.Core;
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
        private set => _serviceProvider = value;
    }

    private static ServiceProvider InitializeServiceProvider()
    {
        var services = new ServiceCollection();
        services.AddSingleton<Repository>();
        services.AddSingleton<CurrenciesService>();
        services.AddSingleton<IStockLogic, StockLogic>();
        services.AddSingleton<IAmazonDynamoDB, AmazonDynamoDBClient>();
        services.AddSingleton<IStockDB, StockDynamoDb>();
        services.AddSingleton<IHttpHandler, HttpHandler>();
        services.AddSingleton<ICurrencyConverter, CurrencyConverterHttpClient>();
        services.AddSingleton<IServiceConfiguration, ServiceEnvironmentConfiguration>();
        services.AddSingleton<IHttpClient, HttpClientWrapper>();

        return services.BuildServiceProvider();
    }
}

public class Functions
{
    private readonly IHttpHandler? _handler;

    public Functions()
    {
        _handler = DI.ServiceProvider.GetRequiredService<IHttpHandler>();
    }

    public Functions(IHttpHandler handler)
    {
        _handler = handler;
    }

    public APIGatewayProxyResponse GetStockById(APIGatewayProxyRequest request, ILambdaContext context)
    {
        context.Logger.LogInformation("Get Request\n");
        var getValueResult = request.PathParameters.TryGetValue("StockId", out var stockId);
        if (!getValueResult || stockId == null)
        {
            return new APIGatewayProxyResponse
            {
                StatusCode = (int)HttpStatusCode.BadRequest,
                Body = "Status id not found on request"
            };
        }

        context.Logger.LogInformation($"StockId:{stockId}");

        var result = _handler.RetrieveStockValues(stockId).Result;

        context.Logger.LogInformation($"result:{result}");

        var response = new APIGatewayProxyResponse
        {
            StatusCode = (int)HttpStatusCode.OK,
            Body = JsonSerializer.Serialize(result),
            Headers = new Dictionary<string, string> { { "Content-Type", "text/json" } }
        };

        return response;
    }
}