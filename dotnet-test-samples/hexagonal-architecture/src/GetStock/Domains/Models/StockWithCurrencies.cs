namespace GetStock.Domains.Models;

public readonly struct StockWithCurrencies
{
    public string StockId { get; }

    public IEnumerable<KeyValuePair<string, double>> Values { get; }

    public StockWithCurrencies(string stockId, IEnumerable<KeyValuePair<string, double>> values)
    {
        StockId = stockId;
        Values = values;
    }

    public override bool Equals(object? obj)
    {
        return obj is StockWithCurrencies currencies &&
               StockId == currencies.StockId &&
               Values.Count() == currencies.Values.Count() && (!Values.Except(currencies.Values).Any() || !currencies.Values.Except(Values).Any());
    }

    public override int GetHashCode() => HashCode.Combine(StockId, Values);
}