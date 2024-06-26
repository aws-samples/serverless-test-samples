using System.Text.Json.Serialization;

namespace ChatbotDemo.Infrastructure.Models.Request;

public class SessionAttributes
{
    [JsonPropertyName("string")] public string Value { get; set; }
}