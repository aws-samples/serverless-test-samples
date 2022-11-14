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
using ServerlessTestApi.Infrastructure;

[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace GetProducts
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
            if (!apigProxyEvent.RequestContext.Http.Method.Equals(HttpMethod.Get.Method))
            {
                return new APIGatewayHttpApiV2ProxyResponse
                {
                    Body = "Only GET allowed",
                    StatusCode = (int)HttpStatusCode.MethodNotAllowed,
                };
            }

            try
            {
                this._logger.LogInformation($"Received {apigProxyEvent}");

                var products = await _dataAccess.GetAllProducts();
    
                context.Logger.LogLine($"Found {products.Products.Count} product(s)");
    
                return new APIGatewayHttpApiV2ProxyResponse
                {
                    Body = JsonSerializer.Serialize(products),
                    StatusCode = 200,
                    Headers = new Dictionary<string, string> {{"Content-Type", "application/json"}}
                };
            }
            catch (Exception e)
            {
                this._logger.LogError(e, "Failure retrieving products");
                
                return new APIGatewayHttpApiV2ProxyResponse
                {
                    StatusCode = 500,
                    Headers = new Dictionary<string, string> {{"Content-Type", "application/json"}}
                };
            }
        }
    }
}
