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
        
    public string Id { get; init; }
        
    public string Name { get; init; }
        
    public decimal Price { get; init; }
}