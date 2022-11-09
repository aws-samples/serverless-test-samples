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

namespace GetProduct
{
    public class Function
    {
        private readonly ProductsDAO _dataAccess;
        private readonly ILogger<Function> _logger;
        
        public Function()
        {
            this._dataAccess = Startup.ServiceProvider.GetRequiredService<ProductsDAO>();
            this._logger = Startup.ServiceProvider.GetRequiredService<ILogger<Function>>();
        }

        internal Function(ProductsDAO dataAccess = null, ILogger<Function> logger = null)
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
                var id = apigProxyEvent.PathParameters["id"];

                var product = await _dataAccess.GetProduct(id);

                if (product == null)
                {
                    return new APIGatewayHttpApiV2ProxyResponse
                    {
                        Body = "Product not found",
                        StatusCode = (int)HttpStatusCode.BadRequest,
                    };
                }

                return new APIGatewayHttpApiV2ProxyResponse
                {
                    StatusCode = (int)HttpStatusCode.OK,
                    Body = JsonSerializer.Serialize(product),
                    Headers = new Dictionary<string, string> {{"Content-Type", "application/json"}}
                };
            }
            catch (Exception e)
            {
                this._logger.LogError(e, "Failure retrieving product");
        
                return new APIGatewayHttpApiV2ProxyResponse
                {
                    StatusCode = (int)HttpStatusCode.InternalServerError,
                };
            }
        }
    }
}
