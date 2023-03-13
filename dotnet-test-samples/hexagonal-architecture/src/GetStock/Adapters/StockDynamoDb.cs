using System.Text.Json;
using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.DocumentModel;
using GetStock.Adapters.Exceptions;

namespace GetStock.Adapters
{
    internal class StockDynamoDb : IStockDB
    {
        private readonly string _tableName;
        private readonly IAmazonDynamoDB _dynamoDbClient;

        public StockDynamoDb(IAmazonDynamoDB dynamoDbClient, IServiceConfiguration configuration)
        {
            _tableName = configuration.DynamoDbTableName;
            _dynamoDbClient = dynamoDbClient;
        }

        public async Task<StockData> GetStockValueAsync(string stockId)
        {
            var table = Table.LoadTable(_dynamoDbClient, _tableName);

            var document = await table.GetItemAsync(stockId);
            if(document == null)
            {
                throw new StockNotFoundException(stockId);
            }
            var jsonString = document.ToJson();

            return JsonSerializer.Deserialize<StockData>(jsonString);
        }

    }
}
