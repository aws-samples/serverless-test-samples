using Microsoft.Extensions.DependencyInjection;
using Amazon.S3;
using ServerlessTestSamples.Core.Services;
using ServerlessTestSamples.Core.Queries;
using Serilog;
using Serilog.Formatting.Compact;

namespace ServerlessTestSamples.Integrations;

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

        services.AddSingleton<IAmazonS3>(new AmazonS3Client());
        services.AddSingleton<IStorageService, S3StorageService>();
        services.AddSingleton<ListStorageAreasQueryHandler>();

        _serviceProvider = services.BuildServiceProvider();
    }
}