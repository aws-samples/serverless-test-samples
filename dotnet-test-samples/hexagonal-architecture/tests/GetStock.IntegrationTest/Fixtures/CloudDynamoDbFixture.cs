using Amazon;
using Amazon.DynamoDBv2;

namespace GetStock.IntegrationTest.Fixtures;

public class CloudDynamoDbFixture
{
    public IAmazonDynamoDB Client { get; }
    private static readonly RegionEndpoint DbRegion = RegionEndpoint.USEast1;

    public CloudDynamoDbFixture()
    {
        Client = new AmazonDynamoDBClient(DbRegion);
    }
}