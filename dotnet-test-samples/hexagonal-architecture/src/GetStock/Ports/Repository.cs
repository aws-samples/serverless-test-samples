using GetStock.Adapters;

namespace GetStock.Ports;

internal class Repository
{
    private readonly IStockDB _stockDb;

    public Repository(IStockDB stockDb)
    {
        _stockDb = stockDb;
    }

    public async Task<double> GetStockValue(string stockId)
    {
        var stockData = await _stockDb.GetStockValueAsync(stockId);

        return stockData.Value;
    }
}