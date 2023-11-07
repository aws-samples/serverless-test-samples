namespace ApiTests.IntegrationTest.Drivers
{
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
        
        public decimal Price { get; set; }
    }
}