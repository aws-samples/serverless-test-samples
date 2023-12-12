using System.Text.Json.Serialization;

namespace CreateCustomerFunction;

using AWS.Lambda.Powertools.Tracing;

public record CreateCustomerCommandResponse
{
    [JsonPropertyName("firstName")]
    public string? FirstName { get; init; }
    
    [JsonPropertyName("lastName")]
    public string? LastName { get; init; }
    
    [JsonPropertyName("address")]
    public string? Address { get; init; }
    
    [JsonPropertyName("success")]
    public bool Success { get; init; }
}

