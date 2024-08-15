using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.Model;

namespace GetStock.IntegrationTest.Fixtures
{
    public class DynamoDbTestBase : IClassFixture<DynamoDbFixture>, IDisposable
    {
        private const string TableNamePrefix = "test-stocks";
        protected string TableName { get; }
        protected IAmazonDynamoDB Client { get; }

        protected DynamoDbTestBase(DynamoDbFixture fixture)
        {
            TableName = $"{TableNamePrefix}{Guid.NewGuid()}";
            Client = fixture.Client;

            var request = new CreateTableRequest
            {
                TableName = TableName,
                AttributeDefinitions = [new AttributeDefinition("StockId", "S")],
                KeySchema = [new KeySchemaElement("StockId", KeyType.HASH)],
                ProvisionedThroughput = new ProvisionedThroughput { ReadCapacityUnits = 1, WriteCapacityUnits = 1 }
            };

            Client.CreateTableAsync(request).Wait();
            
            WaitUntilDynamoDbActive().Wait();
        }

        private async Task WaitUntilDynamoDbActive()
        {
            int sleepDuration = 2000;

            var describeTableRequest = new DescribeTableRequest
            {
                TableName = TableName
            };

            TableStatus status;
            
            do
            {
                Thread.Sleep(sleepDuration);

                var describeTableResponse = await Client.DescribeTableAsync(describeTableRequest);
                status = describeTableResponse.Table.TableStatus;

                Console.Write(".");
            }
            while (status != TableStatus.ACTIVE);
        }

        public void Dispose()
        {
            Client.DeleteTableAsync(TableName).Wait();
        }
    }
}

