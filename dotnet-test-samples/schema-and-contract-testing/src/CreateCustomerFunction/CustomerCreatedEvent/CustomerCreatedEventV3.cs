namespace CreateCustomerFunction.CustomerCreatedEvent;

using Newtonsoft.Json;

using SchemaTesting.Shared;

// Different versions of the same event are used to demonstrate how test failures
// are caused by schema changes
public class CustomerCreatedEventV3 : BaseCustomerCreatedEvent
{
    [JsonProperty("customerId")]
    public string? CustomerId { get; set; }
    
    [JsonProperty("address")]
    public string? Address { get; set; }

    [JsonProperty("type")]
    public override string Type => "CustomerCreatedEventV3";
}