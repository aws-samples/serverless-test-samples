using Microsoft.Extensions.DependencyInjection;

namespace GetStock.Adapters;

public static class AdapterExtensions
{
    public static void AddAdapters(this IServiceCollection services)
    {
        services.AddSingleton<ICurrencyConverter, CurrencyConverterHttpClient>();
        services.AddSingleton<IHttpClient, HttpClientWrapper>();
        services.AddSingleton<IServiceConfiguration, ServiceEnvironmentConfiguration>();
        services.AddSingleton<IStockDB, StockDynamoDb>();
    }
}