namespace ServerlessTestApi.Core.Models;

public record ProductDTO
{
    public ProductDTO()
    {
    }

    public ProductDTO(string id, string name, decimal price)
    {
        this.Id = id;
        this.Name = name;
        this.Price = price;
    }
        
    public string Id { get; set; }
        
    public string Name { get; set; }
        
    public decimal Price { get; set; }
}