using System;
using System.Text.Json.Serialization;

namespace ServerlessTestApi.Core.Models
{
    public class Product
    {
        public Product()
        {
        }

        public Product(string id, string name, decimal price)
        {
            this.Id = id;
            this.Name = name;
            this.Price = price;
        }
        
        public string Id { get; set; }
        
        public string Name { get; set; }
        
        [JsonPropertyName("Price")]
        public decimal Price { get; private set; }

        public void SetPrice(decimal newPrice)
        {
            this.Price = Math.Round(newPrice, 2);
        }

        public override string ToString()
        {
            return "Product{" +
                   "id='" + this.Id + '\'' +
                   ", name='" + this.Name + '\'' +
                   ", price=" + this.Price +
                   '}';
        }

        public ProductDTO AsDTO() => new ProductDTO(this.Id, this.Name, this.Price);
    }
}