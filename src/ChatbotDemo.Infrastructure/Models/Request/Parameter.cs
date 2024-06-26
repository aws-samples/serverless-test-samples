using System.Text.Json.Serialization;

namespace ChatbotDemo.Infrastructure.Models.Request;

public class Parameter
{
    [JsonPropertyName("name")] public string Name { get; set; }
    [JsonPropertyName("type")] public string Type { get; set; }
    [JsonPropertyName("value")] public string Value { get; set; }
}