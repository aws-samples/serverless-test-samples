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

namespace GetProduct;

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

        if (!apigProxyEvent.PathParameters.TryGetValue("id", out var id))
        {
            return new()
            {
                Body = "Product not found",
                StatusCode = (int)HttpStatusCode.NotFound,
            };
        }

        ProductDTO product;

        using (var cts = context.GetCancellationTokenSource())
        {
            try
            {
                product = await _dataAccess.GetProduct(id, cts.Token);
            }
            catch (OperationCanceledException e)
            {
                _logger.LogError(e, "Retrieving product timed out");

                return new()
                {
                    StatusCode = (int)HttpStatusCode.ServiceUnavailable,
                };
            }
            catch (Exception e)
            {
                _logger.LogError(e, "Failure retrieving product");

                return new()
                {
                    StatusCode = (int)HttpStatusCode.InternalServerError,
                };
            }
        }

        if (product == null)
        {
            return new()
            {
                Body = "Product not found",
                StatusCode = (int)HttpStatusCode.NotFound,
            };
        }

        return new()
        {
            StatusCode = (int)HttpStatusCode.OK,
            Body = JsonSerializer.Serialize(product, _jsonOptions.Value),
            Headers = new Dictionary<string, string> { ["Content-Type"] = "application/json" },
        };
    }
}
