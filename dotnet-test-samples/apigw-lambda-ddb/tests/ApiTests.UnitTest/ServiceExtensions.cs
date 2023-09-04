using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.Model;
using FakeItEasy;
using Microsoft.Extensions.DependencyInjection;
using ServerlessTestApi.Infrastructure.DataAccess;

namespace ApiTests.UnitTest;

public static class ServiceExtensions
{
    public static IServiceCollection AddMockServices(this IServiceCollection services)
    {
        return services.AddSingleton(CreateFakeDynamoDb);
    }

    private static IAmazonDynamoDB CreateFakeDynamoDb(IServiceProvider serviceProvider)
    {
        var item = ProductMapper.ProductToDynamoDb(new("testid", "Test Product", 10));
        var fakeDynamoDb = A.Fake<IAmazonDynamoDB>();

        A.CallTo(() => 
                fakeDynamoDb.ScanAsync(A<ScanRequest>._, A<CancellationToken>._))
                .Returns(
                    Task.FromResult(
                    new ScanResponse { Items = new(capacity: 1) { item } }));

        
        A.CallTo(() => 
                fakeDynamoDb.GetItemAsync(A<GetItemRequest>._, A<CancellationToken>._))
                .Returns(Task.FromResult(
                    new GetItemResponse()
                {
                    IsItemSet = true,
                    Item = item,
                }));

        A.CallTo(() => 
                fakeDynamoDb.PutItemAsync(A<string>._, A<Dictionary<string, AttributeValue>>._, A<CancellationToken>._))
                .Returns(Task.FromResult(new PutItemResponse()));

        A.CallTo(() => 
                fakeDynamoDb.DeleteItemAsync(A<string>._, A<Dictionary<string, AttributeValue>>._, A<CancellationToken>._))
                .Returns(Task.FromResult(new DeleteItemResponse()));

        return fakeDynamoDb;
    }
}