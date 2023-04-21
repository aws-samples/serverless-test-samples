using Amazon.Lambda.Core;

namespace GetStock.Adapters;

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
            return string.Empty;
        }

        return await response.Content.ReadAsStringAsync();
    }

    public void Dispose()
    {
        _httpClient?.Dispose();
    }
}