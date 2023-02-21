using HexagonalArchitecture.Ports;

namespace HexagonalArchitecture.Domains
{
    internal record StockWithCurrencies(string StockId)
    {
        public IDictionary<string, double> Values { get; } = new Dictionary<string, double>();
    }

    internal class StockLogic
    {
        private const string BaseCurrency = "EUR";
        private static readonly string[] Currencies = new[] { "USD", "CAD", "AUD" };

        private readonly Repository _repository;
        private readonly CurrenciesService _currency;

        public StockLogic(Repository repository, CurrenciesService currency)
        {
            _repository = repository;
            _currency = currency;
        }

        public async Task<StockWithCurrencies> RetrieveStockValues(string stockId)
        {
            var stockValue = await _repository.GetStockValue(stockId);
            var currencyList = await _currency.GetCurrencyData(BaseCurrency, Currencies);

            var stockWithCurrencies = new StockWithCurrencies(stockId);
            stockWithCurrencies.Values.Add(BaseCurrency, stockValue);
            foreach (var pair in currencyList)
            {
                stockWithCurrencies.Values[pair.Key] = stockValue * pair.Value;
            }

            return stockWithCurrencies;
        }
    }
}
