using System.Text.Json;
using Amazon.DynamoDBv2;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using Microsoft.Extensions.Options;
using SqsEventHandler.Repositories;
using SqsEventHandler.Repositories.Models;

namespace SqsEventHandler.Infrastructure;

public static class Startup
{
    private static IServiceProvider? _serviceProvider;

    public static IServiceProvider ServiceProvider => _serviceProvider ??= InitializeServiceProvider();

    private static void AddDefaultServices(IServiceCollection services)
    {
        var builder = new ConfigurationBuilder()
            .AddInMemoryCollection(
                new Dictionary<string, string?>()
                {
                    ["EMPLOYEE_TABLE_NAME"] = "Employees",
                })
            .AddEnvironmentVariables();

        IConfiguration configuration = builder.Build();

        services.Configure<DynamoDbOptions>(configuration);
        services.TryAddSingleton(configuration);
        services.TryAddSingleton(static _ =>
            Options.Create(new JsonSerializerOptions(JsonSerializerDefaults.Web)));
        services.TryAddTransient<IValidateOptions<DynamoDbOptions>, DynamoDbOptionsValidator>();
        services.TryAddSingleton<IAmazonDynamoDB>(static _ => new AmazonDynamoDBClient());
        services.TryAddSingleton<IDynamoDbRepository<EmployeeDto>, EmployeeRepository>();
    }

    private static IServiceProvider InitializeServiceProvider()
    {
        var services = new ServiceCollection();
        AddDefaultServices(services);
        return services.BuildServiceProvider();
    }
}