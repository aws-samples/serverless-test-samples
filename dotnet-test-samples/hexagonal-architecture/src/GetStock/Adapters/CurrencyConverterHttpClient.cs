using System.Text.Json;
using AWS.Lambda.Powertools.Logging;
using GetStock.Adapters.Model;

namespace GetStock.Adapters;

public class CurrencyConverterHttpClient : ICurrencyConverter, IDisposable
{
    private readonly IHttpClient _httpHandler;

    public CurrencyConverterHttpClient(IHttpClient httpHandler)
    {
        _httpHandler = httpHandler;
    }

    public void Dispose()
    {
        _httpHandler.Dispose();
    }

    public async Task<IDictionary<string, double>> GetCurrencies(string baseCurrency, IEnumerable<string> currencies)
    {
        var currencyList = string.Join(",", currencies);

        var requestUrl = $"?symbols={currencyList}&base={baseCurrency}";
        var responseJson = await _httpHandler.GetAsync(requestUrl);
        //TODO: chgeck for empty result
        Logger.LogInformation("response: " + responseJson);

        var result = JsonSerializer.Deserialize<CurrencyRates>(responseJson);
        if (result is not { Success: true })
        {
            return new Dictionary<string, double>();
        }

        return result.Rates;
    }
}