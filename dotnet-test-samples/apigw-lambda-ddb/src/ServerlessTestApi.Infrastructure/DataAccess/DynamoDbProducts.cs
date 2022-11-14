using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.Model;
using ServerlessTestApi.Core.DataAccess;
using ServerlessTestApi.Core.Models;

namespace ServerlessTestApi.Infrastructure.DataAccess
{
    public class DynamoDbProducts : IProductsDAO
    {
        private static string PRODUCT_TABLE_NAME = Environment.GetEnvironmentVariable("PRODUCT_TABLE_NAME") ?? throw new ArgumentException("PRODUCT_TABLE_NAME environment variable is null");
        private readonly IAmazonDynamoDB _dynamoDbClient;

        public DynamoDbProducts(IAmazonDynamoDB dynamoDbClient)
        {
            this._dynamoDbClient = dynamoDbClient;
        }
        
        public async Task<ProductDTO?> GetProduct(string id)
        {
            var getItemResponse = await this._dynamoDbClient.GetItemAsync(new GetItemRequest(PRODUCT_TABLE_NAME,
                new Dictionary<string, AttributeValue>(1)
                {
                    {ProductMapper.PK, new AttributeValue(id)}
                }));
            
            var product = getItemResponse.IsItemSet ? ProductMapper.ProductFromDynamoDB(getItemResponse.Item): null;

            return product?.AsDTO();
        }

        public async Task PutProduct(Product product)
        {
            await this._dynamoDbClient.PutItemAsync(PRODUCT_TABLE_NAME, ProductMapper.ProductToDynamoDb(product));
        }

        public async Task DeleteProduct(string id)
        {
            await this._dynamoDbClient.DeleteItemAsync(PRODUCT_TABLE_NAME, new Dictionary<string, AttributeValue>(1)
            {
                {ProductMapper.PK, new AttributeValue(id)}
            });
        }

        public async Task<ProductWrapper> GetAllProducts()
        {
            var data = await this._dynamoDbClient.ScanAsync(new ScanRequest()
            {
                TableName = PRODUCT_TABLE_NAME,
                Limit = 20
            });

            var products = new List<ProductDTO>();

            foreach (var item in data.Items)
            {
                products.Add(ProductMapper.ProductFromDynamoDB(item).AsDTO());
            }

            return new ProductWrapper(products);
        }
    }
}