using System;
using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.Model;

namespace GetStock.IntegrationTest.Fixtures
{
    public class DynamoDbTestBase : IClassFixture<DynamoDbFixture>, IDisposable
    {
        private const string _tableNamePrefix = "test-stocks";
        protected string TableName { get; }
        protected IAmazonDynamoDB Client { get; }

        public DynamoDbTestBase(string tableNamePrefix, LocalDynamoDbFixture fixture)
        {
            TableName = $"{_tableNamePrefix}{Guid.NewGuid().ToString()}";
            Client = fixture.Client;

            var request = new CreateTableRequest
            {
                TableName = TableName,
                AttributeDefinitions = new List<AttributeDefinition>
                {
                    new("StockId", "S")
                },
                KeySchema = new List<KeySchemaElement> { new("StockId", Amazon.DynamoDBv2.KeyType.HASH) },
                ProvisionedThroughput = new ProvisionedThroughput { ReadCapacityUnits = 1, WriteCapacityUnits = 1 }
            };

            Client.CreateTableAsync(request).Wait();
        }

        public void Dispose()
        {
            Client.DeleteTableAsync(TableName).Wait();
        }
    }
}

