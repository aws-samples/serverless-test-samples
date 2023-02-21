using HexagonalArchitecture.Adapters;

namespace HexagonalArchitecture.Ports
{
    internal class CurrenciesService
    {
        private readonly ICurrencyConverter _currencyConverter;

        public CurrenciesService(ICurrencyConverter currencyConverter)
        {
            _currencyConverter = currencyConverter;
        }

        public async Task<IDictionary<string, double>> GetCurrencyData(string baseCurrency, IEnumerable<string> currencies)
        {
            return await _currencyConverter.GetCurrencies(baseCurrency, currencies);
        }
    }
}
