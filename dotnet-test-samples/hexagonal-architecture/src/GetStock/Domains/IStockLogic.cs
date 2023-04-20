using GetStock.Domains.Models;

namespace GetStock.Domains;

public interface IStockLogic
{
    Task<StockWithCurrencies> RetrieveStockValuesAsync(string stockId);
}