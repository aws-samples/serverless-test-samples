using System.Text.Json.Serialization;
using ChatbotDemo.Infrastructure.Models.Request;

namespace ChatbotDemo.Infrastructure.Models.Response;

public interface IBedrockResponse
{
    [JsonPropertyName("messageVersion")] string MessageVersion { get; set; }

    [JsonPropertyName("sessionAttributes")]
    SessionAttributes SessionAttributes { get; set; }

    [JsonPropertyName("promptSessionAttributes")]
    PromptSessionAttributes PromptSessionAttribute { get; set; }
}