namespace GetStock.Adapters
{
    public record StockData
    {
        public string StockId { get; set; } = null!;
        public double Value { get; set; }
    }
    public interface IStockDB
    {
        Task<StockData> GetStockValueAsync(string stockId);
    }
}