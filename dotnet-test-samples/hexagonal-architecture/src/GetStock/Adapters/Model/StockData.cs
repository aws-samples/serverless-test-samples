namespace GetStock.Adapters.Model;

public record StockData
{
    public string StockId { get; set; } = null!;
    public double Value { get; set; }
}