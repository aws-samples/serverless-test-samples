using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.Model;
using Microsoft.Extensions.DependencyInjection;
using Moq;
using ServerlessTestApi.Infrastructure.DataAccess;

namespace ApiTests.UnitTest;

public static class ServiceExtensions
{
    public static IServiceCollection AddMockServices(this IServiceCollection services)
    {
        return services.AddSingleton(NewMockDynamoDB);
    }

    private static IAmazonDynamoDB NewMockDynamoDB(IServiceProvider serviceProvider)
    {
        var item = ProductMapper.ProductToDynamoDb(new("testid", "Test Product", 10));
        var dynamoDb = new Mock<IAmazonDynamoDB>();

        dynamoDb.Setup(ddb => ddb.ScanAsync(It.IsAny<ScanRequest>(), It.IsAny<CancellationToken>()))
                .ReturnsAsync(new ScanResponse() { Items = new(capacity: 1) { item } });

        dynamoDb.Setup(p => p.GetItemAsync(It.IsAny<GetItemRequest>(), It.IsAny<CancellationToken>()))
                .ReturnsAsync(new GetItemResponse()
                {
                    IsItemSet = true,
                    Item = item,
                });

        dynamoDb.Setup(p => p.PutItemAsync(It.IsAny<string>(), It.IsAny<Dictionary<string, AttributeValue>>(), It.IsAny<CancellationToken>()))
                .ReturnsAsync(new PutItemResponse());

        dynamoDb.Setup(p => p.DeleteItemAsync(It.IsAny<string>(), It.IsAny<Dictionary<string, AttributeValue>>(), It.IsAny<CancellationToken>()))
                .ReturnsAsync(new DeleteItemResponse());

        return dynamoDb.Object;
    }
}