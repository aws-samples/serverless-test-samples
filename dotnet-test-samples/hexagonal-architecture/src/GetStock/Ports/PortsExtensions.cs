using Microsoft.Extensions.DependencyInjection;

namespace GetStock.Ports;

public static class PortsExtensions
{
    public static void AddPortsServices(this IServiceCollection services)
    {
        services.AddSingleton<Repository>();
        services.AddSingleton<CurrenciesService>();
        services.AddSingleton<IHttpHandler, HttpHandler>();
    }
}