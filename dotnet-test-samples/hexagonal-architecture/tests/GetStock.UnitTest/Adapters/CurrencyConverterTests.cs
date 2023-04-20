using GetStock.Adapters;

namespace GetStock.UnitTest
{
    public class CurrencyConverterTests
    {
        [Fact]
        public async Task GetCurrencies_returnFailure_returnEmptyList()
        {
            var fakeClient = A.Fake<IHttpClient>();
            A.CallTo(() => fakeClient.GetAsync(A<string>._))
                .Returns(Task.FromResult(
    @"{
  ""base"": ""EUR"",
  ""date"": ""2023-01-24"",
  ""rates"": {    
    ""USD"": 1.2345
  },
  ""success"": false,
  ""timestamp"": 1674556804
}"
            ));

            var target = new CurrencyConverterHttpClient(fakeClient);
            var result = await target.GetCurrencies("", Array.Empty<string>());
            var expected = new Dictionary<string, double> { };

            Assert.Equal(expected, result);
        }

        [Fact]
        public async Task GetCurrencies_returnSuccessWithJsonString_returnDeserializedValues()
        {
            var response = new HttpResponseMessage();
            var fakeClient = A.Fake<IHttpClient>();
            A.CallTo(() => fakeClient.GetAsync(A<string>._))
                .Returns(Task.FromResult(
    @"{
  ""base"": ""EUR"",
  ""date"": ""2023-01-24"",
  ""rates"": {    
    ""USD"": 1.2345
  },
  ""success"": true,
  ""timestamp"": 1674556804
}"
            ));

            var target = new CurrencyConverterHttpClient(fakeClient);
            var result = await target.GetCurrencies("", Array.Empty<string>());

            var expected = new Dictionary<string, double> {
            { "USD", 1.2345 }
        };

            Assert.Equal(expected, result);
        }

        [Fact]
        public async Task GetCurrencies_returnSuccessWithMultipleValues_returnAllValues()
        {
            var response = new HttpResponseMessage();
            var fakeClient = A.Fake<IHttpClient>();
            A.CallTo(() => fakeClient.GetAsync(A<string>._))
                .Returns(Task.FromResult(
    @"{
  ""base"": ""EUR"",
  ""date"": ""2023-01-24"",
  ""rates"": {    
    ""AUD"": 1.111,
    ""CAD"": 2.222,
    ""USD"": 3.333
  },
  ""success"": true,
  ""timestamp"": 1674556804
}"));

            var target = new CurrencyConverterHttpClient(fakeClient);
            var result = await target.GetCurrencies("", Array.Empty<string>());

            var expected = new Dictionary<string, double> {
            { "AUD", 1.111 },
            { "CAD", 2.222 },
            { "USD", 3.333 }
        };

            Assert.Equal(expected, result);
        }
    }
}