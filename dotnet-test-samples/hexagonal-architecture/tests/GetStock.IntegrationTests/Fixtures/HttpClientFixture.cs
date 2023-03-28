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
            //TODO: insert API key from https://fixer.io/
            CurrencyApiKey = "", 
            CurrencyBaseAddress = "https://api.apilayer.com/fixer/latest"
        };

        Client = new HttpClientWrapper(configuration);
    }

    public void Dispose()
    {
        Client.Dispose();
    }
}