using System;
using System.Collections.Generic;
using System.Text.Json;
using System.Text.Json.Serialization;
using Amazon.DynamoDBv2;
using Amazon.XRay.Recorder.Handlers.AwsSdk;
using ChatbotDemo.Repositories;
using ChatbotDemo.Repositories.Models;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using Microsoft.Extensions.Options;

namespace ChatbotDemo.Infrastructure;

public static class Startup
{
    private static IServiceProvider _serviceProvider;

    public static IServiceProvider ServiceProvider => _serviceProvider ??= InitializeServiceProvider();

    private static void AddDefaultServices(IServiceCollection services)
    {
        AWSSDKHandler.RegisterXRayForAllServices();
        var builder = new ConfigurationBuilder()
            .AddInMemoryCollection(
                new Dictionary<string, string>()
                {
                    ["CONNECTION_TABLE_NAME"] = "Connections",
                }!)
            .AddEnvironmentVariables();

        IConfiguration configuration = builder.Build();

        services.Configure<ApplicationConfigurationOptions>(configuration);
        services.TryAddSingleton(configuration);
        services.TryAddSingleton(static _ =>
            Options.Create(new JsonSerializerOptions
            {
                DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
            }));
        services.TryAddTransient<IValidateOptions<ApplicationConfigurationOptions>, ApplicationConfigurationsValidator>();
        services.TryAddSingleton<IAmazonDynamoDB>(static _ => new AmazonDynamoDBClient());
        services.TryAddSingleton<IDynamoDbRepository<ConnectionDto>, ConnectionRepository>();
    }

    private static IServiceProvider InitializeServiceProvider()
    {
        var services = new ServiceCollection();
        AddDefaultServices(services);
        return services.BuildServiceProvider();
    }
}