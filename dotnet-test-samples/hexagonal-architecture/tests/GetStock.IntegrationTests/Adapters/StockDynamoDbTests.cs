using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.DocumentModel;
using Amazon.DynamoDBv2.Model;
using GetStock.Adapters;
using GetStock.Adapters.Exceptions;
using GetStock.IntegrationTest.Fixtures;
using GetStock.IntegrationTest.TestUtilities;

namespace GetStock.IntegrationTest.Adapters;

[Collection("Local DynamoDB collection")]
public class StockDynamoDbTests : IDisposable
{
    private readonly AmazonDynamoDBClient _client;
    private static readonly string TableName = "test-stocks";

    public StockDynamoDbTests(LocalDynamoDbFixture fixture)
    {        
        _client = fixture.Client;
        var request = new CreateTableRequest
        {
            TableName = TableName,
            AttributeDefinitions = new List<AttributeDefinition>
            {
                new("StockId", "S"),
                //new("Value", "N")
            },
            KeySchema = new List<KeySchemaElement> { new("StockId", Amazon.DynamoDBv2.KeyType.HASH) },
            ProvisionedThroughput = new ProvisionedThroughput { ReadCapacityUnits = 1, WriteCapacityUnits = 1 }
        };

        _client.CreateTableAsync(request).Wait();
    }

    public void Dispose()
    {
        _client.DeleteTableAsync(TableName).Wait();
    }

    [Fact]
    public async Task GetStockValue_StockNotFound_ThrowStockNotFoundException()
    {
        var config = new TestServiceConfiguration
        {
            DynamoDbTableName = TableName
        };

        var target = new StockDynamoDb(_client, config);

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
        
        var table = Table.LoadTable(_client, TableName);
                await table.PutItemAsync(item);

        var target = new StockDynamoDb(_client, config);

        var result = await target.GetStockValueAsync("stock-1");

        var expected = new StockData { StockId = "stock-1", Value =100.0 };

        Assert.Equal(expected, result);
    }
}
