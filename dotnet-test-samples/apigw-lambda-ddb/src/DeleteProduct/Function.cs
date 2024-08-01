using Amazon.Lambda.APIGatewayEvents;
using Amazon.Lambda.Core;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using ServerlessTestApi.Core.DataAccess;
using ServerlessTestApi.Infrastructure;
using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;

[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace DeleteProduct;

public class Function
{
    private readonly IProductsDao _dataAccess;
    private readonly ILogger<Function> _logger;

    public Function() : this(Startup.ServiceProvider) { }

    public Function(IProductsDao dataAccess, ILogger<Function> logger)
        : this(NewServiceProvider(dataAccess, logger)) { }

    private Function(IServiceProvider serviceProvider)
    {
        _dataAccess = serviceProvider.GetRequiredService<IProductsDao>();
        _logger = serviceProvider.GetRequiredService<ILogger<Function>>();
    }

    private static IServiceProvider NewServiceProvider(IProductsDao dataAccess, ILogger<Function> logger)
    {
        var container = new System.ComponentModel.Design.ServiceContainer();

        container.AddService(typeof(IProductsDao), dataAccess);
        container.AddService(typeof(ILogger<Function>), logger);

        return container;
    }

    public async Task<APIGatewayHttpApiV2ProxyResponse> FunctionHandler(
        APIGatewayHttpApiV2ProxyRequest apigProxyEvent,
        ILambdaContext context)
    {
        var method = new HttpMethod(apigProxyEvent.RequestContext.Http.Method);

        if (!method.Equals(HttpMethod.Delete))
        {
            return new()
            {
                Body = "Only DELETE allowed",
                StatusCode = (int)HttpStatusCode.MethodNotAllowed,
                Headers = new Dictionary<string, string>()
                {
                    ["Allow"] = HttpMethod.Delete.Method,
                    ["Content-Type"] = "text/plain",
                },
            };
        }

        // DELETE is idempotent; no 'id' or an nonexistent product simply do nothing
        if (!apigProxyEvent.PathParameters.TryGetValue("id", out var id))
        {
            return new() { StatusCode = (int)HttpStatusCode.NoContent };
        }

        using var cts = context.GetCancellationTokenSource();

        try
        {
            await _dataAccess.DeleteProduct(id, cts.Token);

            return new()
            {
                StatusCode = (int)HttpStatusCode.OK,
                Body = $"Product with id {id} deleted",
                Headers = new Dictionary<string, string>() { ["Content-Type"] = "text/plain" },
            };
        }
        catch (OperationCanceledException)
        {
            return new()
            {
                StatusCode = (int)HttpStatusCode.ServiceUnavailable,
            };
        }
        catch (Exception e)
        {
            context.Logger.LogLine($"Error deleting product {e.Message} {e.StackTrace}");

            return new()
            {
                StatusCode = (int)HttpStatusCode.InternalServerError,
            };
        }
    }
}