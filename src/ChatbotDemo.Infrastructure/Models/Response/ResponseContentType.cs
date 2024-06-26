using System.Text.Json.Serialization;

namespace ChatbotDemo.Infrastructure.Models.Response;

public record ResponseContentType
{
    [JsonPropertyName("body")]
    public string Body { get; set; }
}