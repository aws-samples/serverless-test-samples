using System.Globalization;
using Amazon.DynamoDBv2.Model;
using ServerlessTestApi.Core.Models;

namespace ServerlessTestApi.Infrastructure.DataAccess
{
    public class ProductMapper
    {
        public static string PK = "id";
        public static string NAME = "name";
        public static string PRICE = "price";
        
        public static Product ProductFromDynamoDB(Dictionary<String, AttributeValue> items) {
            var product = new Product(items[PK].S, items[NAME].S, decimal.Parse(items[PRICE].N));

            return product;
        }
        
        public static Dictionary<String, AttributeValue> ProductToDynamoDb(Product product) {
            Dictionary<String, AttributeValue> item = new Dictionary<string, AttributeValue>(3);
            item.Add(PK, new AttributeValue(product.Id));
            item.Add(NAME, new AttributeValue(product.Name));
            item.Add(PRICE, new AttributeValue()
            {
                N = product.Price.ToString(CultureInfo.InvariantCulture)
            });

            return item;
        }
    }
}