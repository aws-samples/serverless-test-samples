using System.Net;
using System.Text.Json;
using Amazon.DynamoDBv2;
using Amazon.Lambda.APIGatewayEvents;
using Amazon.Lambda.Core;
using GetStock.Adapters;
using GetStock.Domains;
using GetStock.Ports;
using Microsoft.Extensions.DependencyInjection;

namespace GetStock;

public class Functions
{
    private readonly IHttpHandler _handler;

    public Functions()
    {
        var serviceCollection = new ServiceCollection();

        serviceCollection.AddSingleton<IAmazonDynamoDB, AmazonDynamoDBClient>();
        serviceCollection.AddSingleton<IHttpClient, HttpClientWrapper>();
        serviceCollection.AddSingleton<IStockDB, StockDynamoDb>();
        serviceCollection.AddSingleton<ICurrencyConverter, CurrencyConverterHttpClient>();
        serviceCollection.AddSingleton<IStockLogic, StockLogic>();


        var serviceProvider = serviceCollection.BuildServiceProvider();

        _handler = serviceProvider.GetService<HttpHandler>();
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

        var result = _handler.RetrieveStockValues(stockId).Result;
        var response = new APIGatewayProxyResponse
        {
            StatusCode = (int)HttpStatusCode.OK,
            Body = JsonSerializer.Serialize(result),
            Headers = new Dictionary<string, string> { { "Content-Type", "text/json" } }
        };

        return response;
    }
}