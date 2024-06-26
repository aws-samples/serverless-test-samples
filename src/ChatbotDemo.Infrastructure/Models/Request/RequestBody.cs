using System.Text.Json.Serialization;

namespace ChatbotDemo.Infrastructure.Models.Request;

public class RequestBody
{
    [JsonPropertyName("content")]
    public Content Content { get; set; }
}