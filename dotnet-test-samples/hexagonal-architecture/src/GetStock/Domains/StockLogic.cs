using Amazon.Lambda.Core;
using GetStock.Adapters.Exceptions;
using GetStock.Domains.Models;
using GetStock.Ports;
using static GetStock.Utilities.CollectionUtils;

namespace GetStock.Domains
{
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
