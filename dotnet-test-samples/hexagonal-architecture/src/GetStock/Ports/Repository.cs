using HexagonalArchitecture.Adapters;

namespace HexagonalArchitecture.Ports;

internal class Repository
{
    private readonly IStockDB _stockDb;

    public Repository(IStockDB stockDb)
    {
        _stockDb = stockDb;
    }

    public async Task<double> GetStockValue(string stockId)
    {
        var stockData = await _stockDb.GetStockValue(stockId);

        return stockData.Value;
    }
}