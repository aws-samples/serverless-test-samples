namespace SchemaTesting.SchemaRegistry;

using CreateCustomerFunction;

using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

public static class SampleEventReader
{
    public static async Task<CustomerCreatedEvent?> ParseEventVersion(string eventVersion)
    {
        var eventJson = await File.ReadAllTextAsync($"./events/event-{eventVersion}.json");
        
        return JsonConvert.DeserializeObject<CustomerCreatedEvent>(eventJson);
    }
    
    public static async Task<JObject> ParseRawJsonFromEventVersion(string eventVersion)
    {
        var eventJson = await File.ReadAllTextAsync($"./events/event-{eventVersion}.json");

        return JObject.Parse(eventJson);
    }
}