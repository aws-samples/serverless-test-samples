namespace ServerlessTestApi;

using System.Collections.Generic;
using System.Text.Json;

using Amazon.DynamoDBv2;
using Amazon.Lambda.Annotations;
using Amazon.XRay.Recorder.Handlers.AwsSdk;

using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using Microsoft.Extensions.Options;

using Serilog;
using Serilog.Formatting.Compact;

using ServerlessTestApi.Core.DataAccess;
using ServerlessTestApi.Infrastructure;
using ServerlessTestApi.Infrastructure.DataAccess;

[LambdaStartup]
public class Startup
{
    public void ConfigureServices(IServiceCollection services)
    {
        AWSSDKHandler.RegisterXRayForAllServices();

        var builder = new ConfigurationBuilder()
            .AddInMemoryCollection(
                new Dictionary<string, string>()
                {
                    ["PRODUCT_TABLE_NAME"] = "Products",
                })
            .AddEnvironmentVariables();

        var logger = new LoggerConfiguration()
            .WriteTo.Console(new RenderedCompactJsonFormatter())
            .CreateLogger();

        IConfiguration configuration = builder.Build();

        services.Configure<DynamoDbOptions>(configuration);
        services.TryAddSingleton(configuration);
        services.TryAddSingleton(static sp => Options.Create(new JsonSerializerOptions(JsonSerializerDefaults.Web)));
        services.TryAddTransient<IValidateOptions<DynamoDbOptions>, DynamoDbOptionsValidator>();
        services.AddLogging(builder => builder.AddSerilog(logger));
        services.TryAddSingleton<IAmazonDynamoDB>(static sp => new AmazonDynamoDBClient());
        services.TryAddSingleton<IProductsDAO, DynamoDbProducts>();
    }
}