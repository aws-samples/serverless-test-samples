using FluentAssertions;
using GetStock.Adapters;
using GetStock.IntegrationTest.Fixtures;
using GetStock.IntegrationTest.TestUtilities;

namespace GetStock.IntegrationTest.Adapters
{
    public class HttpClientTests : IClassFixture<HttpClientFixture>
    {
        static HttpClientTests()
        {
            Environment.SetEnvironmentVariable("");
        }

        public HttpClientTests() : base(
            new TestServiceConfiguration
            {
                CurrencyApiKey = "", //TODO: insert API key from https://fixer.io/
                CurrencyBaseAddress = "https://api.apilayer.com/fixer/latest"
            }
            )
        {
        }

        [Fact]
        public async Task GetCurrencies_passCurrenciesToConvert_ReturnRates()
        {
            var target = new CurrencyConverterHttpClient(Client);

            var result = await target.GetCurrencies("USD", new[] { "EUR", "CAD", "GBP" });

            result.Keys.Should().BeEquivalentTo("EUR", "CAD", "GBP");
        }
    }
}
