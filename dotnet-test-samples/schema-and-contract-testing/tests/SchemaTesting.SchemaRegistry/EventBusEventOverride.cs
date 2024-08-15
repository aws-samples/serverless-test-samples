namespace SchemaTesting.SchemaRegistry;

using Amazon.EventBridge.Model;

using Newtonsoft.Json;

using Shared;

/// <summary>
/// Schemas stored in EventBridge Schema Registry include the <see cref="PutEventsRequestEntry"/> wrapper.
/// This class allows defaults to be set for validating the schema of the object within the Detail property.
/// </summary>
/// <typeparam name="T">The type of <see cref="Event"/> being checked.</typeparam>
public class EventBusEventOverride<T> : PutEventsRequestEntry where T : Event
{
    public EventBusEventOverride(object eventObject)
    {
        var evt = (T)eventObject;
        
        Detail = new EventWrapper(evt);
        
        Id = Guid.NewGuid().ToString();
        DetailType = evt.Type;
        Resources = [];
        Source = "com.customer";
        EventBusName = "custom-event-bus";
        Time = DateTime.Now;
        Region = "eu-west-1";
        Version = "1";
        Account = "12345678";
    }
    
    [JsonProperty("detail")]
    public new object Detail { get; set; }
    
    [JsonProperty("detail-type")]
    public new string DetailType { get; set; }
    
    [JsonProperty("resources")]
    public new object[] Resources { get; set; }
    
    [JsonProperty("id")]
    public string Id { get; set; }
    
    [JsonProperty("source")]
    public new string Source { get; set; }
    
    [JsonProperty("time")]
    public new DateTime Time { get; set; }
    
    [JsonProperty("region")]
    public string Region { get; set; }
    
    [JsonProperty("version")]
    public string Version { get; set; }
    
    [JsonProperty("account")]
    public string Account { get; set; }
}