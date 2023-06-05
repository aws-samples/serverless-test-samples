using FluentAssertions;
using GetStock.Adapters;
using GetStock.IntegrationTest.Fixtures;

namespace GetStock.IntegrationTest.Adapters;

public class HttpClientTests : IClassFixture<HttpClientFixture>
{
    private readonly HttpClientFixture _fixture;


    public HttpClientTests(HttpClientFixture fixture)
    {
        _fixture = fixture;
    }
       
    [Fact]
    public async Task GetCurrencies_With_CurrenciesToConvert_Should_ReturnRates()
    {
        var target = new CurrencyConverterHttpClient(_fixture.Client);

        var result = await target.GetCurrencies("USD", new[] { "EUR", "CAD", "GBP" });

        result.Keys.Should().BeEquivalentTo("EUR", "CAD", "GBP");
    }
}