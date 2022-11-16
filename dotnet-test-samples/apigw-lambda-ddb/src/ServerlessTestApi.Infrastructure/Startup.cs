using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
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
                _serviceProvider = InitializeServiceProvider();
            }

            return _serviceProvider;
        }
        private set => _serviceProvider = value;
    }

    private static ServiceProvider InitializeServiceProvider()
    {
        var services = new ServiceCollection();
        
        var logger = new LoggerConfiguration()
            .WriteTo.Console(new RenderedCompactJsonFormatter())
            .CreateLogger();
        
        services.AddLogging(builder =>
        {
            builder.AddSerilog(logger);
        });

        if (Environment.GetEnvironmentVariable("USE_MOCKS") == "true")
        {
            logger.Warning("WARNING! Application is running using mock implementations");

            services.AddMockServices();
        }
        else
        {
            services.AddInfrastructureServices();
        }
        
        services.AddSingleton<IProductsDAO, DynamoDbProducts>();

        return services.BuildServiceProvider();
    }
}