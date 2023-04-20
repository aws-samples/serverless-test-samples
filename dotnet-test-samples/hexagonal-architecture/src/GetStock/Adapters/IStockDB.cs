using GetStock.Adapters.Model;

namespace GetStock.Adapters
{
    public interface IStockDB
    {
        Task<StockData> GetStockValueAsync(string stockId);
    }
}