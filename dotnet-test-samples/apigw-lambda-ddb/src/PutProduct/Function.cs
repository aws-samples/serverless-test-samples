using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;

using Amazon.Lambda.APIGatewayEvents;
using Amazon.Lambda.Core;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using ServerlessTestApi.Core.DataAccess;
using ServerlessTestApi.Core.Models;
using ServerlessTestApi.Infrastructure;

[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace PutProduct
{
    public class Function
    {
        private readonly IProductsDAO _dataAccess;
        private readonly ILogger<Function> _logger;
        public Function()
        {
            this._dataAccess = Startup.ServiceProvider.GetRequiredService<IProductsDAO>();
            this._logger = Startup.ServiceProvider.GetRequiredService<ILogger<Function>>();
        }

        internal Function(IProductsDAO dataAccess = null, ILogger<Function> logger = null)
        {
            this._dataAccess = dataAccess;
            this._logger = logger;
        }

        public async Task<APIGatewayHttpApiV2ProxyResponse> FunctionHandler(APIGatewayHttpApiV2ProxyRequest apigProxyEvent,
            ILambdaContext context)
        {
            if (!apigProxyEvent.RequestContext.Http.Method.Equals(HttpMethod.Put.Method))
            {
                return new APIGatewayHttpApiV2ProxyResponse
                {
                    Body = "Only PUT allowed",
                    StatusCode = (int)HttpStatusCode.MethodNotAllowed,
                };
            }

            if (string.IsNullOrEmpty(apigProxyEvent.Body))
            {
                return new APIGatewayHttpApiV2ProxyResponse
                {
                    Body = "No body contents",
                    StatusCode = (int)HttpStatusCode.BadRequest,
                };
            }
                
            try
            {
                var id = apigProxyEvent.PathParameters["id"];

                var product = JsonSerializer.Deserialize<ProductDTO>(apigProxyEvent.Body);

                if (product == null || id != product.Id)
                {
                    return new APIGatewayHttpApiV2ProxyResponse
                    {
                        Body = "Product ID in the body does not match path parameter",
                        StatusCode = (int)HttpStatusCode.BadRequest,
                    };
                }

                await _dataAccess.PutProduct(new Product(product.Id, product.Name, product.Price));
        
                return new APIGatewayHttpApiV2ProxyResponse
                {
                    StatusCode = (int)HttpStatusCode.Created,
                    Body = $"Created product with id {id}"
                };
            }
            catch (Exception e)
            {
                context.Logger.LogLine($"Error creating product {e.Message} {e.StackTrace}");
        
                return new APIGatewayHttpApiV2ProxyResponse
                {
                    Body = "Not Found",
                    StatusCode = (int)HttpStatusCode.InternalServerError,
                };
            }
        }
    }
}
