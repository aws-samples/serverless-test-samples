namespace GetStock.Adapters;

public interface ICurrencyConverter
{
    Task<IDictionary<string, double>> GetCurrencies(string baseCurrency, IEnumerable<string> currencies);
}