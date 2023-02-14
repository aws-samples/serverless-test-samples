using Amazon.S3;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using Microsoft.Extensions.Options;
using Serilog;
using Serilog.Formatting.Compact;
using ServerlessTestSamples.Core.Queries;
using ServerlessTestSamples.Core.Services;
using System.Text.Json;

namespace ServerlessTestSamples.Integrations;

public static class Startup
{
    private static IServiceProvider? _serviceProvider;

    public static IServiceProvider ServiceProvider => _serviceProvider ??= NewServiceProvider();

    public static void AddDefaultServices(IServiceCollection services)
    {
        var logger = new LoggerConfiguration()
            .WriteTo.Console(new RenderedCompactJsonFormatter())
            .CreateLogger();

        services.AddLogging();
        services.TryAddSingleton(static sp => Options.Create(new JsonSerializerOptions(JsonSerializerDefaults.Web)));
        services.TryAddSingleton<IAmazonS3>(static sp => new AmazonS3Client());
        services.TryAddSingleton<IStorageService, S3StorageService>();
        services.TryAddSingleton<ListStorageAreasQueryHandler>();
    }

    private static IServiceProvider NewServiceProvider()
    {
        var services = new ServiceCollection();
        AddDefaultServices(services);
        return services.BuildServiceProvider();
    }
}