using System;
using System.Text.Json.Serialization;

namespace ServerlessTestApi.Core.Models;

public class Product
{
    public Product(string id, string name, decimal price)
    {
        Id = id;
        Name = name;
        Price = price;
    }
    
    public string Id { get; set; }
    
    public string Name { get; set; }
    
    [JsonPropertyName(nameof(Price))]
    public decimal Price { get; private set; }

    public void SetPrice(decimal newPrice) => Price = Math.Round(newPrice, 2);

    public override string ToString() =>
        $"Product{{id='{Id}', name='{Name}', price={Price}}}";

    public ProductDTO AsDTO() => new(Id, Name, Price);
}