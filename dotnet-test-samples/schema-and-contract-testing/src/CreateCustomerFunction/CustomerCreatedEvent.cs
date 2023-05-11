namespace CreateCustomerFunction;

using Newtonsoft.Json;

using SchemaTesting.Shared;

public abstract class CustomerCreatedEvent : Event {}

// Different versions of the same event are used to demonstrate how test failures
// are caused by schema changes
public class CustomerCreatedEventV1 : CustomerCreatedEvent
{
    [JsonProperty("customerId")]
    public string? CustomerId { get; set; }
    
    [JsonProperty("firstName")]
    public string? FirstName { get; set; }
    
    [JsonProperty("lastName")]
    public string? LastName { get; set; }
    
    [JsonProperty("address")]
    public string? Address { get; set; }

    [JsonProperty("type")]
    public override string Type => "CustomerCreatedEventV1";
}

public class CustomerCreatedEventV2: CustomerCreatedEvent
{
    [JsonProperty("customerId")]
    public string? CustomerId { get; set; }
    
    [JsonProperty("firstName")]
    public string? FirstName { get; set; }
    
    [JsonProperty("lastName")]
    public string? LastName { get; set; }
    
    [JsonProperty("address")]
    public string? Address { get; set; }
    
    [JsonProperty("email")]
    public string? Email { get; set; }

    [JsonProperty("type")]
    public override string Type => "CustomerCreatedEventV2";
}

public class CustomerCreatedEventV3 : CustomerCreatedEvent
{
    [JsonProperty("customerId")]
    public string? CustomerId { get; set; }
    
    [JsonProperty("address")]
    public string? Address { get; set; }

    [JsonProperty("type")]
    public override string Type => "CustomerCreatedEventV3";
}