using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.Net.Http;
using System.Text.Json;
using Amazon.Lambda.Core;
using Amazon.Lambda.APIGatewayEvents;
using Amazon.S3;
using System;
using System.Net;
using Amazon.XRay.Recorder.Core;
using Amazon.XRay.Recorder.Handlers.AwsSdk;
using Amazon.XRay.Recorder.Handlers.System.Net;
using ServerlessTestSamples.Core.Queries;
using ServerlessTestSamples.Integrations;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

// Assembly attribute to enable the Lambda function's JSON input to be converted into a .NET class.
[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace ServerlessTestSamples
{
    public class Function
    {
        private static ListStorageAreasQueryHandler _queryHandler;
        private static ILogger<Function> _logger;

        public Function() : this(null, null)
        {
        }

        internal Function(ListStorageAreasQueryHandler handler, ILogger<Function> logger)
        {
            AWSSDKHandler.RegisterXRayForAllServices();
            
            _queryHandler = handler ?? Startup.ServiceProvider.GetRequiredService<ListStorageAreasQueryHandler>();
            _logger = logger ?? Startup.ServiceProvider.GetRequiredService<ILogger<Function>>();
        }

        public async Task<APIGatewayProxyResponse> Handler(APIGatewayProxyRequest apigProxyEvent,
            ILambdaContext context)
        {
            try
            {
                var queryResult = await _queryHandler.Handle(new ListStorageAreasQuery());

                return new APIGatewayProxyResponse
                {
                    Body = JsonSerializer.Serialize(queryResult),
                    StatusCode = 200,
                    Headers = new Dictionary<string, string> {{"Content-Type", "application/json"}}
                };
            }
            catch (AmazonS3Exception e)
            {
                context.Logger.LogLine(e.Message);
                context.Logger.LogLine(e.StackTrace);

                return new APIGatewayProxyResponse
                {
                    Body = "[]",
                    StatusCode = 500,
                    Headers = new Dictionary<string, string> {{"Content-Type", "application/json"}}
                };
            }
        }
    }
}