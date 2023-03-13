using Amazon.Lambda.Core;
using GetStock.Adapters.Exceptions;
using GetStock.Ports;
using static GetStock.Utilities.CollectionUtils;

namespace GetStock.Domains
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

        public override int GetHashCode() => HashCode.Combine(StockId, Values);
    }

    public interface IStockLogic
    {
        Task<StockWithCurrencies> RetrieveStockValuesAsync(string stockId);
    }

    internal class StockLogic : IStockLogic
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

        public async Task<StockWithCurrencies> RetrieveStockValuesAsync(string stockId)
        {
            try
            {
                var stockValue = await _repository.GetStockValueAsync(stockId);

                var currencyList = await _currency.GetCurrencyDataAsync(BaseCurrency, Currencies);
                var currencyValues = new List<KeyValuePair<string, double>>(currencyList.Count + 1)
                { 
                    ToPair(BaseCurrency, stockValue)
                };

                currencyValues.AddRange(currencyList.Select(currency => ToPair(currency.Key, stockValue * currency.Value)));

                return new StockWithCurrencies(stockId, currencyValues);
            }
            catch (StockNotFoundException exc)
            {
                LambdaLogger.Log(exc.Message);
             
                return new StockWithCurrencies(stockId, Array.Empty<KeyValuePair<string, double>>());
            }
        }
    }
}
