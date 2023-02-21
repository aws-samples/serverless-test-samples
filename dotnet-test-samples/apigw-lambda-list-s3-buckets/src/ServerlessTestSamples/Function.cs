using Amazon.Lambda.APIGatewayEvents;
using Amazon.Lambda.Core;
using Amazon.S3;
using Amazon.XRay.Recorder.Handlers.AwsSdk;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using ServerlessTestSamples.Core.Queries;
using ServerlessTestSamples.Integrations;
using System;
using System.Collections.Generic;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;

// Assembly attribute to enable the Lambda function's JSON input to be converted into a .NET class.
[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace ServerlessTestSamples
{
    public class Function
    {
        private readonly ListStorageAreasQueryHandler _queryHandler;
        private readonly ILogger<Function> _logger;
        private readonly IOptions<JsonSerializerOptions> _jsonOptions;

        public Function() : this(Startup.ServiceProvider) { }

        public Function(
            ListStorageAreasQueryHandler handler,
            ILogger<Function> logger,
            IOptions<JsonSerializerOptions> jsonOptions)
            : this(NewServiceProvider(handler, logger, jsonOptions)) { }

        private Function(IServiceProvider serviceProvider)
        {
            _queryHandler = serviceProvider.GetRequiredService<ListStorageAreasQueryHandler>();
            _logger = serviceProvider.GetRequiredService<ILogger<Function>>();
            _jsonOptions = serviceProvider.GetRequiredService<IOptions<JsonSerializerOptions>>();
            AWSSDKHandler.RegisterXRayForAllServices();
        }

        private static IServiceProvider NewServiceProvider(
            ListStorageAreasQueryHandler handler,
            ILogger<Function> logger,
            IOptions<JsonSerializerOptions> jsonOptions)
        {
            var container = new System.ComponentModel.Design.ServiceContainer();

            container.AddService(typeof(ListStorageAreasQueryHandler), handler);
            container.AddService(typeof(ILogger<Function>), logger);
            container.AddService(typeof(IOptions<JsonSerializerOptions>), jsonOptions);

            return container;
        }

        public async Task<APIGatewayProxyResponse> Handler(
            APIGatewayProxyRequest apigProxyEvent,
            ILambdaContext context)
        {
            using var cts = new CancellationTokenSource();

            if (context.RemainingTime >= TimeSpan.Zero)
            {
                // RemainingTime is the amount of time before Lambda terminates the function.
                // we don't want to go right to the end so we pad the end. if not otherwise
                // specified, use 0.25% of the remaining time. this ensures gives a relative
                // amount of time to gracefully cancel before we are destructively aborted.
                // adjust to your needs accordingly
                var beforeAbort = TimeSpan.FromSeconds(context.RemainingTime.TotalSeconds * 0.0025);
                cts.CancelAfter(context.RemainingTime.Subtract(beforeAbort));
            }

            try
            {
                var queryResult = await _queryHandler.Handle(new(), cts.Token);

                return new()
                {
                    Body = JsonSerializer.Serialize(queryResult, _jsonOptions.Value),
                    StatusCode = 200,
                    Headers = new Dictionary<string, string> { ["Content-Type"] = "application/json" },
                };
            }
            catch (AmazonS3Exception e)
            {
                context.Logger.LogLine(e.Message);
                context.Logger.LogLine(e.StackTrace);

                return new() { StatusCode = 500 };
            }
        }
    }
}