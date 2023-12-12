using Amazon.DynamoDBv2.Model;
using ServerlessTestApi.Core.Models;
using System.Globalization;

namespace ServerlessTestApi.Infrastructure.DataAccess;

public class ProductMapper
{
    public const string PK = "id";
    public const string Name = "name";
    public const string Price = "price";

    public static Product ProductFromDynamoDB(Dictionary<string, AttributeValue> items) =>
        new(items[PK].S, items[Name].S, decimal.Parse(items[Price].N, CultureInfo.InvariantCulture));

    public static Dictionary<string, AttributeValue> ProductToDynamoDb(Product product) =>
        new(capacity: 3)
        {
            [PK] = new(product.Id),
            [Name] = new(product.Name),
            [Price] = new() { N = product.Price.ToString(CultureInfo.InvariantCulture) },
        };
}