namespace GetStock.Adapters.Exceptions;

public class StockNotFoundException : Exception
{
    public StockNotFoundException()
    {
        
    }
    public StockNotFoundException(string stockId) : base($"Stock {stockId} not found")
    {
    }
}