using Microsoft.Extensions.DependencyInjection;

namespace GetStock.Domains;

public static class DomainExtensions
{
    public static void AddDomainServices(this IServiceCollection services)
    {
        services.AddSingleton<IStockLogic, StockLogic>();
    }
}