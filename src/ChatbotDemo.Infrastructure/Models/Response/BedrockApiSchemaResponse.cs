using System.Text.Json.Serialization;
using ChatbotDemo.Infrastructure.Models.Request;

namespace ChatbotDemo.Infrastructure.Models.Response;

public class BedrockApiSchemaResponse : IBedrockResponse
{
    [JsonPropertyName("messageVersion")] public string MessageVersion { get; set; }

    [JsonPropertyName("sessionAttributes")]
    public SessionAttributes SessionAttributes { get; set; }

    [JsonPropertyName("promptSessionAttribute")]
    public PromptSessionAttributes PromptSessionAttribute { get; set; }

    [JsonPropertyName("response")] public ApiSchemaResponse Response { get; set; }
}