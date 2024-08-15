using Amazon.DynamoDBv2;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using Microsoft.Extensions.Options;
using Serilog;
using Serilog.Formatting.Compact;
using ServerlessTestApi.Core.DataAccess;
using ServerlessTestApi.Infrastructure.DataAccess;
using System.Text.Json;

namespace ServerlessTestApi.Infrastructure;

public static class Startup
{
    private static IServiceProvider? _serviceProvider;

    public static IServiceProvider ServiceProvider => _serviceProvider ??= InitializeServiceProvider();

    public static void AddDefaultServices(IServiceCollection services)
    {
        var builder = new ConfigurationBuilder()
            .AddInMemoryCollection(
                new Dictionary<string, string?>()
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
        services.TryAddSingleton<IProductsDao, DynamoDbProducts>();
    }

    private static IServiceProvider InitializeServiceProvider()
    {
        var services = new ServiceCollection();
        AddDefaultServices(services);
        return services.BuildServiceProvider();
    }
}