using System.Text.Json;
using Amazon.XRay.Recorder.Handlers.AwsSdk;
using ExampleApi.Repositories.Sql;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using Microsoft.Extensions.Options;

namespace ExampleApi.Infrastructure;

public static class Startup
{
    private static IServiceProvider? _serviceProvider;

    public static IServiceProvider ServiceProvider => _serviceProvider ??= InitializeServiceProvider();

    private static void AddDefaultServices(IServiceCollection services)
    {
        AWSSDKHandler.RegisterXRayForAllServices();
        var builder = new ConfigurationBuilder()
            .AddInMemoryCollection(
                new Dictionary<string, string?>()
                {
                    ["SQL_CONNECTION_STRING_SECRET_NAME"] = "localhost",
                })
            .AddEnvironmentVariables();

        IConfiguration configuration = builder.Build();

        services.Configure<SqlServerOptions>(configuration);
        services.TryAddSingleton(configuration);
        services.TryAddSingleton(static _ =>
            Options.Create(new JsonSerializerOptions(JsonSerializerDefaults.Web)));
        services.TryAddTransient<IValidateOptions<SqlServerOptions>, SqlServerOptionsValidator>();
        services.TryAddSingleton<IEmployeeRepository, EmployeeRepository>();
    }

    private static IServiceProvider InitializeServiceProvider()
    {
        var services = new ServiceCollection();
        AddDefaultServices(services);
        return services.BuildServiceProvider();
    }
}