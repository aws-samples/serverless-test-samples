using Amazon.Lambda.APIGatewayEvents;
using Amazon.Lambda.Core;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using ServerlessTestApi.Core.DataAccess;
using ServerlessTestApi.Core.Models;
using ServerlessTestApi.Infrastructure;
using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;

[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace GetProducts;

public class Function
{
    private readonly IProductsDAO _dataAccess;
    private readonly IOptions<JsonSerializerOptions> _jsonOptions;
    private readonly ILogger<Function> _logger;

    public Function() : this(Startup.ServiceProvider) { }

    public Function(
        IProductsDAO dataAccess,
        ILogger<Function> logger,
        IOptions<JsonSerializerOptions> jsonOptions)
        : this(NewServiceProvider(dataAccess, logger, jsonOptions)) { }

    private Function(IServiceProvider serviceProvider)
    {
        _dataAccess = serviceProvider.GetRequiredService<IProductsDAO>();
        _jsonOptions = serviceProvider.GetRequiredService<IOptions<JsonSerializerOptions>>();
        _logger = serviceProvider.GetRequiredService<ILogger<Function>>();
    }

    private static IServiceProvider NewServiceProvider(
        IProductsDAO dataAccess,
        ILogger<Function> logger,
        IOptions<JsonSerializerOptions> jsonOptions)
    {
        var container = new System.ComponentModel.Design.ServiceContainer();

        container.AddService(typeof(IProductsDAO), dataAccess);
        container.AddService(typeof(IOptions<JsonSerializerOptions>), jsonOptions);
        container.AddService(typeof(ILogger<Function>), logger);

        return container;
    }

    public async Task<APIGatewayHttpApiV2ProxyResponse> FunctionHandler(
        APIGatewayHttpApiV2ProxyRequest apigProxyEvent,
        ILambdaContext context)
    {
        var method = new HttpMethod(apigProxyEvent.RequestContext.Http.Method);

        if (!method.Equals(HttpMethod.Get))
        {
            return new()
            {
                Body = "Only GET allowed",
                StatusCode = (int)HttpStatusCode.MethodNotAllowed,
                Headers = new Dictionary<string, string> { ["Allow"] = HttpMethod.Get.Method },
            };
        }

        _logger.LogInformation($"Received {apigProxyEvent}");

        ProductWrapper products;

        using (var cts = context.GetCancellationTokenSource())
        {
            try
            {
                products = await _dataAccess.GetAllProducts(cts.Token);
            }
            catch (OperationCanceledException e)
            {
                _logger.LogError(e, "Retrieving products timed out");

                return new()
                {
                    StatusCode = (int)HttpStatusCode.ServiceUnavailable,
                };
            }
            catch (Exception e)
            {
                _logger.LogError(e, "Failure retrieving products");

                return new()
                {
                    StatusCode = (int)HttpStatusCode.InternalServerError,
                };
            }
        }

        context.Logger.LogLine($"Found {products.Products.Count} product(s)");

        return new()
        {
            Body = JsonSerializer.Serialize(products, _jsonOptions.Value),
            StatusCode = (int)HttpStatusCode.OK,
            Headers = new Dictionary<string, string> { { "Content-Type", "application/json" } }
        };
    }
}