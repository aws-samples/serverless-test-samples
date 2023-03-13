using Amazon.DynamoDBv2.DocumentModel;
using GetStock.Adapters;
using GetStock.Adapters.Exceptions;
using GetStock.IntegrationTest.Fixtures;
using GetStock.IntegrationTest.TestUtilities;

namespace GetStock.IntegrationTest.Adapters;

public class StockDynamoDbTests : DynamoDbTestBase
{
    public StockDynamoDbTests(DynamoDbFixture fixture)
        : base("test-stocks", fixture)
    {
    }

    [Fact]
    public async Task GetStockValue_StockNotFound_ThrowStockNotFoundException()
    {
        var config = new TestServiceConfiguration
        {
            DynamoDbTableName = TableName
        };

        var target = new StockDynamoDb(Client, config);

        await Assert.ThrowsAsync<StockNotFoundException>(() => target.GetStockValueAsync("stock-1"));
    }

    [Fact]
    public async Task GetStockValue_StockFound_ReturnStockData()
    {
        var config = new TestServiceConfiguration
        {
            DynamoDbTableName = TableName
        };

        var item = new Document();
        item["StockId"] = "stock-1";
        item["Value"] = 100.0;

        var table = Table.LoadTable(Client, TableName);
        await table.PutItemAsync(item);

        var target = new StockDynamoDb(Client, config);

        var result = await target.GetStockValueAsync("stock-1");

        var expected = new StockData { StockId = "stock-1", Value = 100.0 };

        Assert.Equal(expected, result);
    }
}
