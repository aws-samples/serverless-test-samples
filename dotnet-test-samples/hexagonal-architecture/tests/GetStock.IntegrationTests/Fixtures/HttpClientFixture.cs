using GetStock.Adapters;
using GetStock.IntegrationTest.TestUtilities;

namespace GetStock.IntegrationTest.Fixtures;

public class HttpClientFixture : IDisposable
{
    public IHttpClient Client { get; }
    public HttpClientFixture()
    {
        var configuration = new TestServiceConfiguration
        {
            CurrencyApiKey = "", //TODO: insert API key from https://fixer.io/
            CurrencyBaseAddress = "https://api.apilayer.com/fixer/latest"
        };

        Client = new HttpClientWrapper(configuration);
    }

    public void Dispose()
    {
        Client.Dispose();
    }
}