using GetStock.Adapters;
using GetStock.Adapters.Exceptions;
using GetStock.Adapters.Model;
using GetStock.Domains;
using GetStock.Domains.Models;
using static GetStock.Utilities.CollectionUtils;

namespace GetStock.UnitTest.Domains
{
    public class StockLogicTests
    {
        [Fact]
        public async Task RetrieveStockValues_StockFoundInDBNoCurrenciesInService_returnOnlyStockValueInUSD()
        {
            using var fake = new AutoFake();

            var fakeStockDb = fake.Resolve<IStockDB>();
            A.CallTo(() => fakeStockDb.GetStockValueAsync(A<string>._)).Returns(Task.FromResult(new StockData
            {
                StockId = "stock-1",
                Value = 100
            }));

            var fakeCurrencyConverter = fake.Resolve<ICurrencyConverter>();

            IDictionary<string, double> emptyDictionary = new Dictionary<string, double>();
            A.CallTo(() => fakeCurrencyConverter.GetCurrencies(A<string>._, An<IEnumerable<string>>._))
                .Returns(Task.FromResult(emptyDictionary));

            var target = fake.Resolve<StockLogic>();

            var result = await target.RetrieveStockValuesAsync("stock-1");

            var expected = new StockWithCurrencies("stock-1", new[] { ToPair("EUR", 100.0) });

            result.Should().BeEquivalentTo(expected);
        }

        [Fact]
        public async Task RetrieveStockValues_StockFoundInDbCurrenciesReturned_returnListOfCurrencyValues()
        {
            using var fake = new AutoFake();

            var fakeStockDb = fake.Resolve<IStockDB>();
            A.CallTo(() => fakeStockDb.GetStockValueAsync(A<string>._)).Returns(Task.FromResult(new StockData
            {
                StockId = "stock-1",
                Value = 100
            }));

            var fakeCurrencyConverter = fake.Resolve<ICurrencyConverter>();

            IDictionary<string, double> currency = new Dictionary<string, double>
            {
                {"USD", 2 }
            };

            A.CallTo(() => fakeCurrencyConverter.GetCurrencies(A<string>._, An<IEnumerable<string>>._))
                .Returns(Task.FromResult(currency));

            var target = fake.Resolve<StockLogic>();

            var result = await target.RetrieveStockValuesAsync("stock-1");

            var expected = new StockWithCurrencies("stock-1", new[]
            {
                ToPair("EUR", 100.0),
                ToPair("USD", 200.0)
            });

            result.Should().BeEquivalentTo(expected);
        }

        [Fact]
        public async Task RetrieveStockValuesAsync_StockNotFound_ReturnEmptyList()
        {
            using var fake = new AutoFake();

            var fakeStockDb = fake.Resolve<IStockDB>();
            A.CallTo(() => fakeStockDb.GetStockValueAsync(A<string>._))
                .Throws<StockNotFoundException>();

            var target = fake.Resolve<StockLogic>();

            var result = await target.RetrieveStockValuesAsync("stock-1");

            var expected = new StockWithCurrencies("stock-1", Array.Empty<KeyValuePair<string, double>>());

            result.Should().BeEquivalentTo(expected);
        }
    }
}
