using System.Text.Json.Serialization;

namespace ChatbotDemo.Infrastructure.Models.Request;

public class PromptSessionAttributes
{
    [JsonPropertyName("string")] public string Value { get; set; }
}