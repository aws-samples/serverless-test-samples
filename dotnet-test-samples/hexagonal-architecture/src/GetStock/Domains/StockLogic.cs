using HexagonalArchitecture.Ports;
using static GetStock.Utilities.CollectionUtils;

namespace HexagonalArchitecture.Domains
{
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

        public override int GetHashCode()
        {
            return HashCode.Combine(StockId, Values);
        }
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
            var currencyValues = new List<KeyValuePair<string, double>>(currencyList.Count + 1)
            {
                ToPair(BaseCurrency, stockValue)
            };
            currencyValues.AddRange(currencyList.Select(currency => ToPair(currency.Key, stockValue * currency.Value)));

            return new StockWithCurrencies(stockId, currencyValues);            
        }
    }
}
