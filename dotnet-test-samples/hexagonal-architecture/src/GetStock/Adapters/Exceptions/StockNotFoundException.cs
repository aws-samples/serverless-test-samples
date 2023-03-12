namespace GetStock.Adapters.Exceptions;

public class StockNotFoundException : Exception
{
    public StockNotFoundException(string stockId) : base($"Stock {stockId} not found")
    {
    }
}