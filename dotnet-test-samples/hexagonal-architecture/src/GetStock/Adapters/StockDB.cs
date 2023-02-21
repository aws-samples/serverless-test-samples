using System.Text.Json;
using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.DocumentModel;
using GetStock.Adapters;

namespace HexagonalArchitecture.Adapters
{
    internal class StockDynamoDb : IStockDB
    {
        private readonly string _tableName;
        private readonly AmazonDynamoDBClient _dynamoDbClient;

        public StockDynamoDb(AmazonDynamoDBClient dynamoDbClient, IServiceConfiguration configuration)
        {
            _tableName = configuration.DynamoDbTableName;
            _dynamoDbClient = dynamoDbClient;
        }

        public async Task<StockData> GetStockValue(string stockId)
        {
            var table = Table.LoadTable(_dynamoDbClient, _tableName);

            var document = await table.GetItemAsync(stockId);

            var jsonString = document.ToJson();

            return JsonSerializer.Deserialize<StockData>(jsonString);
        }

    }
}
