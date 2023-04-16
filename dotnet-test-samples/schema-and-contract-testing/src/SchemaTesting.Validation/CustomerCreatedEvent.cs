using System.Text.Json.Serialization;

namespace SchemaTesting.Validation;

public abstract class CustomerCreatedEvent: Event{}

public class CustomerCreatedEventV1 : CustomerCreatedEvent
{
    [JsonPropertyName("customerId")]
    public string? CustomerId { get; set; }
    
    [JsonPropertyName("firstName")]
    public string? FirstName { get; set; }
    
    [JsonPropertyName("lastName")]
    public string? LastName { get; set; }
    
    [JsonPropertyName("address")]
    public string? Address { get; set; }
}

public class CustomerCreatedEventV2: CustomerCreatedEvent
{
    [JsonPropertyName("customerId")]
    public string? CustomerId { get; set; }
    
    [JsonPropertyName("firstName")]
    public string? FirstName { get; set; }
    
    [JsonPropertyName("lastName")]
    public string? LastName { get; set; }
    
    [JsonPropertyName("address")]
    public string? Address { get; set; }
    
    [JsonPropertyName("email")]
    public string? Email { get; set; }
}

public class CustomerCreatedEventV3 : CustomerCreatedEvent
{
    [JsonPropertyName("customerId")]
    public string? CustomerId { get; set; }
    
    [JsonPropertyName("address")]
    public string? Address { get; set; }
}