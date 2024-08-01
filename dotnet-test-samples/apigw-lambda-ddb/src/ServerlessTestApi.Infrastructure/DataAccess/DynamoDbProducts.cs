using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.Model;
using Microsoft.Extensions.Options;
using ServerlessTestApi.Core.DataAccess;
using ServerlessTestApi.Core.Models;

namespace ServerlessTestApi.Infrastructure.DataAccess;

public class DynamoDbProducts : IProductsDao
{
    private readonly IAmazonDynamoDB _dynamoDbClient;
    private readonly IOptions<DynamoDbOptions> _options;

    public DynamoDbProducts(IAmazonDynamoDB dynamoDbClient, IOptions<DynamoDbOptions> options)
    {
        _dynamoDbClient = dynamoDbClient;
        _options = options;
    }

    public async Task<ProductDTO?> GetProduct(string id, CancellationToken cancellationToken)
    {
        var response = await _dynamoDbClient.GetItemAsync(
            _options.Value.ProductTableName,
            new(capacity: 1) { [ProductMapper.PK] = new(id) },
            cancellationToken);

        return response.IsItemSet
               ? ProductMapper.ProductFromDynamoDB(response.Item).AsDTO()
               : null;
    }

    public async Task<UpsertResult> PutProduct(Product product, CancellationToken cancellationToken)
    {
        var request = new PutItemRequest()
        {
            TableName = _options.Value.ProductTableName,
            Item = ProductMapper.ProductToDynamoDb(product),
            ReturnValues = ReturnValue.ALL_OLD,
        };
        var response = await _dynamoDbClient.PutItemAsync(request, cancellationToken);
        var hadOldValues = response.Attributes is not null && response.Attributes.Count > 0;

        return hadOldValues ? UpsertResult.Updated : UpsertResult.Inserted;
    }

    public async Task DeleteProduct(string id, CancellationToken cancellationToken)
    {
        await _dynamoDbClient.DeleteItemAsync(
            _options.Value.ProductTableName,
            new(capacity: 1) { [ProductMapper.PK] = new(id) },
            cancellationToken);
    }

    public async Task<ProductWrapper> GetAllProducts(CancellationToken cancellationToken)
    {
        var data = await _dynamoDbClient.ScanAsync(
            new ScanRequest()
            {
                TableName = _options.Value.ProductTableName,
                Limit = 20,
            },
            cancellationToken);
        var products = data.Items
                           .Select(ProductMapper.ProductFromDynamoDB)
                           .Select(static product => product.AsDTO())
                           .ToList();

        return new(products);
    }
}