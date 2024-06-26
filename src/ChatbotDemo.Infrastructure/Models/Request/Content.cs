using System.Text.Json.Serialization;

namespace ChatbotDemo.Infrastructure.Models.Request;

public class Content
{
    [JsonPropertyName("TEXT")] public Text Text { get; set; }
}