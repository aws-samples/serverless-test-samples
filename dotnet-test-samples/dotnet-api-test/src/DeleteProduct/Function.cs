using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Reflection.Metadata;
using System.Text.Json;
using System.Threading.Tasks;

using Amazon.Lambda.APIGatewayEvents;
using Amazon.Lambda.Core;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using ServerlessTestApi.Core.DataAccess;
using ServerlessTestApi.Infrastructure;

[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace DeleteProduct
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
            if (!apigProxyEvent.RequestContext.Http.Method.Equals(HttpMethod.Delete.Method))
            {
                return new APIGatewayHttpApiV2ProxyResponse
                {
                    Body = "Only DELETE allowed",
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

                await _dataAccess.DeleteProduct(product.Id);
        
                return new APIGatewayHttpApiV2ProxyResponse
                {
                    StatusCode = (int)HttpStatusCode.OK,
                    Body = $"Product with id {id} deleted"
                };
            }
            catch (Exception e)
            {
                context.Logger.LogLine($"Error deleting product {e.Message} {e.StackTrace}");
        
                return new APIGatewayHttpApiV2ProxyResponse
                {
                    Body = "Not Found",
                    StatusCode = (int)HttpStatusCode.InternalServerError,
                };
            }
        }
    }
}
