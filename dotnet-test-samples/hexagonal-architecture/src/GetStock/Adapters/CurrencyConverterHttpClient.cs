using System.Text.Json;
using System.Text.Json.Serialization;
using Amazon.Lambda.Core;

namespace GetStock.Adapters
{
    internal class CurrencyRates
    {
        [JsonPropertyName("base")]
        public string Base { get; set; }

        [JsonPropertyName("date")]
        public string Date { get; set; }

        [JsonPropertyName("rates")]
        public Dictionary<string, double> Rates { get; set; }

        [JsonPropertyName("success")]
        public bool Success { get; set; }

        [JsonPropertyName("timestamp")]
        public int Timestamp { get; set; }
    }

    public interface IHttpClient : IDisposable
    {
        Task<string> GetAsync(string url);
    }

    internal class HttpClientWrapper : IHttpClient
    {
        private readonly HttpClient _httpClient;

        public HttpClientWrapper(IServiceConfiguration configuration)
        {
            _httpClient = new HttpClient
            {
                BaseAddress = new Uri(configuration.CurrencyBaseAddress)
            };

            _httpClient.DefaultRequestHeaders.Add("apikey", configuration.CurrencyApiKey);
        }


        public async Task<string> GetAsync(string url)
        {
            var response = await _httpClient.GetAsync(url);
            if (!response.IsSuccessStatusCode)
            {
                LambdaLogger.Log("HTTP call failed: " + response);
                LambdaLogger.Log("URL: " + url);
                return string.Empty;// TODO: exception?
            }

            return await response.Content.ReadAsStringAsync();
        }

        public void Dispose()
        {
            _httpClient?.Dispose();
        }
    }

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
            LambdaLogger.Log("response: " + responseJson);

            var result = JsonSerializer.Deserialize<CurrencyRates>(responseJson);
            if (result == null || !result.Success)
            {
                return new Dictionary<string, double>();
            }

            return result.Rates;
        }
    }
}
