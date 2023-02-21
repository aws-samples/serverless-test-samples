using HexagonalArchitecture.Adapters;

namespace HexagonalArchitecture.Ports;

internal class Repository
{
    private readonly StockDynamoDb _stockDb;

    public Repository(StockDynamoDb stockDb)
    {
        _stockDb = stockDb;
    }

    public async Task<double> GetStockValue(string stockId)
    {
        var stockData = await _stockDb.GetStockValue(stockId);

        return stockData.Value;
    }
}