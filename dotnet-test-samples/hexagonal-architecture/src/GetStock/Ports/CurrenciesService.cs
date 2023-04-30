using GetStock.Adapters;

namespace GetStock.Ports
{
    internal class CurrenciesService
    {
        private readonly ICurrencyConverter _currencyConverter;

        public CurrenciesService(ICurrencyConverter currencyConverter)
        {
            _currencyConverter = currencyConverter;
        }

        public async Task<IDictionary<string, double>> GetCurrencyDataAsync(string baseCurrency, IEnumerable<string> currencies)
        {
            return await _currencyConverter.GetCurrencies(baseCurrency, currencies);
        }
    }
}
