using CreateCustomerFunction;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace SchemaTesting.UnitTest;

using CreateCustomerFunction.CustomerCreatedEvent;

public static class SampleEventReader
{
    public static async Task<BaseCustomerCreatedEvent?> ParseEventVersion(string eventVersion)
    {
        var eventJson = await File.ReadAllTextAsync($"./events/event-{eventVersion}.json");
        
        return JsonConvert.DeserializeObject<BaseCustomerCreatedEvent>(eventJson);
    }
    
    public static async Task<JObject> ParseRawJsonFromEventVersion(string eventVersion)
    {
        var eventJson = await File.ReadAllTextAsync($"./events/event-{eventVersion}.json");

        return JObject.Parse(eventJson);
    }
}