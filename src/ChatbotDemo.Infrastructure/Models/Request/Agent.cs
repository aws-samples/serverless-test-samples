using System.Text.Json.Serialization;

namespace ChatbotDemo.Infrastructure.Models.Request;

public class Agent
{
    [JsonPropertyName("name")] string Name { get; set; }
    [JsonPropertyName("id")] string Id { get; set; }
    [JsonPropertyName("alias")] string Alias { get; set; }
    [JsonPropertyName("version")] string Version { get; set; }
}