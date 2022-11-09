using Amazon.DynamoDBv2;
using Microsoft.Extensions.DependencyInjection;
using Serilog;
using Serilog.Formatting.Compact;
using ServerlessTestApi.Core.DataAccess;
using ServerlessTestApi.Infrastructure.DataAccess;

namespace ServerlessTestApi.Infrastructure;

public static class Startup
{
    private static ServiceProvider? _serviceProvider;

    public static ServiceProvider ServiceProvider
    {
        get
        {
            if (_serviceProvider == null)
            {
                InitializeServiceProvider();
            }

            return _serviceProvider;
        }
        private set => _serviceProvider = value;
    }

    private static void InitializeServiceProvider()
    {
        var services = new ServiceCollection();
        
        var logger = new LoggerConfiguration()
            .WriteTo.Console(new RenderedCompactJsonFormatter())
            .CreateLogger();
        
        services.AddLogging();

        services.AddSingleton<IAmazonDynamoDB>(new AmazonDynamoDBClient());
        services.AddSingleton<ProductsDAO, DynamoDbProducts>();

        _serviceProvider = services.BuildServiceProvider();
    }
}