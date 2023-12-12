namespace ApiTests.IntegrationTestWithEmulation;

using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.Model;
using Amazon.Runtime;

using DotNet.Testcontainers.Containers;

using Microsoft.Extensions.Options;

using ServerlessTestApi.Core.DataAccess;
using ServerlessTestApi.Infrastructure;
using ServerlessTestApi.Infrastructure.DataAccess;

using Testcontainers.DynamoDb;

public sealed class TestStartup : IDisposable
{
    private readonly IContainer container;

    public IProductsDAO ProductsDao { get; }

    public TestStartup()
    {
        this.container = new DynamoDbBuilder()
            // 8000 on the container is bound to a random local port to allow for the same test to run anywhere without fear of port conflicts
            .WithPortBinding(
                8000,
                true)
            .Build();

        this.container.StartAsync().GetAwaiter().GetResult();

        // The GetMappedPublicPort method retrieves the locally mapped port number for port 8000 on the container.
        var serviceUrl = $"http://localhost:{this.container.GetMappedPublicPort(8000)}";
        
        var dynamoDbClient = new AmazonDynamoDBClient(new BasicAWSCredentials("test", "test"), //The DynamoDB SDK requires credentials, but these aren't used.
            new AmazonDynamoDBConfig()
            {
                // Override the ServiceURL using the local version. 
                // IMPORTANT! If you set the RegionEndpoint here that will override any value you set in the ServiceURL.
                ServiceURL = serviceUrl,
            });

        // Create the table using the same schema as defined in the SAM template.
        var createReq = new CreateTableRequest(
            "Products",
            new List<KeySchemaElement>()
            {
                new KeySchemaElement(
                    "id",
                    KeyType.HASH)
            });
        createReq.AttributeDefinitions = new List<AttributeDefinition>(1)
        {
            new AttributeDefinition(
                "id",
                ScalarAttributeType.S)
        };
        createReq.BillingMode = BillingMode.PAY_PER_REQUEST;

        dynamoDbClient.CreateTableAsync(createReq).GetAwaiter().GetResult();

        this.ProductsDao = new DynamoDbProducts(dynamoDbClient, Options.Create(new DynamoDbOptions()
        {
            ProductTableName = "Products"
        }));
    }

    public void Dispose()
    {
        this.container.StopAsync();
    }
}