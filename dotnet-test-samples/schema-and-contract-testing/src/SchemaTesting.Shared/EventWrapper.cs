namespace SchemaTesting.Shared;

using AWS.Lambda.Powertools.Tracing;

using Newtonsoft.Json;

public class EventWrapper
{
    public EventWrapper(Event payload)
    {
        this.Metadata = new();
        this.Payload = payload;
        this.Type = payload.GetType().Name;
    }
    
    [JsonProperty("type")]
    public string Type { get; set; }
    
    [JsonProperty("metadata")]
    public Metadata Metadata { get; set; }

    [JsonProperty("payload")]
    public Event Payload { get; set; }
}

public record Metadata()
{
    [JsonProperty("type")] 
    public string Type { get; set; } = "Metadata";
    
    [JsonProperty("publishDate")]
    public DateTime PublishDate { get; set; } = DateTime.Now;
    
    [JsonProperty("traceIdentifier")]
    public string TraceIdentifier { get; set; } = Tracing.GetEntity().TraceId ?? "test-trace";
}