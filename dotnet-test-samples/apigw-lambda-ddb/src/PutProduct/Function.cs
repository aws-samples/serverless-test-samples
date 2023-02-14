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

namespace PutProduct
{
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

            if (!method.Equals(HttpMethod.Put))
            {
                return new()
                {
                    Body = "Only PUT allowed",
                    StatusCode = (int)HttpStatusCode.MethodNotAllowed,
                    Headers = new Dictionary<string, string> ()
                    {
                        ["Allow"] = HttpMethod.Put.Method,
                        ["Content-Type"] = "text/plain",
                    },
                };
            }

            if (string.IsNullOrEmpty(apigProxyEvent.Body))
            {
                return new()
                {
                    Body = "No body contents",
                    StatusCode = (int)HttpStatusCode.BadRequest,
                    Headers = new Dictionary<string, string>() { ["Content-Type"] = "text/plain" },
                };
            }

            if (!apigProxyEvent.PathParameters.TryGetValue("id", out var id))
            {
                return new()
                {
                    StatusCode = (int)HttpStatusCode.BadRequest,
                };
            }

            UpsertResult result;

            using (var cts = context.GetCancellationTokenSource())
            {
                try
                {
                    var product = JsonSerializer.Deserialize<ProductDTO>(apigProxyEvent.Body, _jsonOptions.Value);

                    if (product == null || (!string.IsNullOrEmpty(product.Id) && product.Id != id))
                    {
                        return new()
                        {
                            Body = "Product ID in the body does not match path parameter",
                            StatusCode = (int)HttpStatusCode.BadRequest,
                            Headers = new Dictionary<string, string>() { ["Content-Type"] = "text/plain" },
                        };
                    }

                    result = await _dataAccess.PutProduct(new(id, product.Name, product.Price), cts.Token);
                }
                catch (OperationCanceledException e)
                {
                    _logger.LogError(e, "Inserting or updating a product timed out");

                    return new()
                    {
                        StatusCode = (int)HttpStatusCode.ServiceUnavailable,
                    };
                }
                catch (Exception e)
                {
                    context.Logger.LogLine($"Error creating product {e.Message} {e.StackTrace}");

                    return new()
                    {
                        StatusCode = (int)HttpStatusCode.InternalServerError,
                    };
                }
            }

            if (result == UpsertResult.Inserted)
            {
                var request = apigProxyEvent.RequestContext;
                var location = new UriBuilder()
                {
                    Scheme = Uri.UriSchemeHttps,
                    Host = request.DomainName,
                    Path = request.Http.Path,
                };

                return new()
                {
                    StatusCode = (int)HttpStatusCode.Created,
                    Body = $"Created product with id {id}",
                    Headers = new Dictionary<string, string>()
                    {
                        ["Content-Type"] = "text/plain",
                        ["Location"] = location.Uri.ToString(),
                    },
                };
            }

            return new()
            {
                StatusCode = (int)HttpStatusCode.OK,
                Body = $"Updated product with id {id}",
                Headers = new Dictionary<string, string>() { ["Content-Type"] = "text/plain" },
            };
        }
    }
}