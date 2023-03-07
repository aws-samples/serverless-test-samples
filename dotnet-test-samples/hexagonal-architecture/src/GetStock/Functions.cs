using Amazon.DynamoDBv2;
using Amazon.Lambda.APIGatewayEvents;
using Amazon.Lambda.Core;
using HexagonalArchitecture.Adapters;
using HexagonalArchitecture.Ports;
using Microsoft.Extensions.DependencyInjection;
using System.Net;
using System.Text.Json;

[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

public class Functions
{
    private readonly HttpHandler _handler;

    public Functions()
    {
        var serviceCollection = new ServiceCollection();

        serviceCollection.AddSingleton<IAmazonDynamoDB, AmazonDynamoDBClient>();
        serviceCollection.AddSingleton<IHttpClient, HttpClientWrapper>();
        serviceCollection.AddSingleton<IStockDB, StockDynamoDb>();
        serviceCollection.AddSingleton<ICurrencyConverter, CurrencyConverterHttpClient>();

        var serviceProvider = serviceCollection.BuildServiceProvider();

        _handler = serviceProvider.GetService<HttpHandler>();
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