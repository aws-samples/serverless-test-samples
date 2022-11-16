using Amazon.DynamoDBv2.Model;
using Amazon.DynamoDBv2;
using Microsoft.Extensions.DependencyInjection;
using Moq;
using ServerlessTestApi.Infrastructure.DataAccess;
using ServerlessTestApi.Core.Models;

namespace ServerlessTestApi.Infrastructure
{
    public static class ServiceExtensions
    {
        public static IServiceCollection AddMockServices(this IServiceCollection services)
        {
            var testProduct = new Product("testid", "Test Product", 10);
            var productAsDynamoDbItem = ProductMapper.ProductToDynamoDb(testProduct);

            var mockDynamoDbClient = new Mock<IAmazonDynamoDB>();
            mockDynamoDbClient.Setup(p => p.ScanAsync(It.IsAny<ScanRequest>(), It.IsAny<CancellationToken>()))
                .ReturnsAsync(new ScanResponse()
                {
                    Items = new List<Dictionary<string, AttributeValue>>(1)
                    {
                    productAsDynamoDbItem
                    }
                });
            mockDynamoDbClient.Setup(p => p.GetItemAsync(It.IsAny<GetItemRequest>(), It.IsAny<CancellationToken>()))
                .ReturnsAsync(new GetItemResponse()
                {
                    IsItemSet = true,
                    Item = productAsDynamoDbItem
                });
            mockDynamoDbClient.Setup(p => p.PutItemAsync(It.IsAny<string>(), It.IsAny<Dictionary<string, AttributeValue>>(), It.IsAny<CancellationToken>()))
                .ReturnsAsync(new PutItemResponse());
            mockDynamoDbClient.Setup(p => p.DeleteItemAsync(It.IsAny<string>(), It.IsAny<Dictionary<string, AttributeValue>>(), It.IsAny<CancellationToken>()))
                .ReturnsAsync(new DeleteItemResponse());

            services.AddSingleton<IAmazonDynamoDB>(mockDynamoDbClient.Object);

            return services;
        }

        public static IServiceCollection AddInfrastructureServices(this IServiceCollection services)
        {
            services.AddSingleton<IAmazonDynamoDB>(new AmazonDynamoDBClient());

            return services;
        }
    }
}
