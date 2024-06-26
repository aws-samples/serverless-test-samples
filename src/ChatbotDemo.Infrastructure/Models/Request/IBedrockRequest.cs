using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace ChatbotDemo.Infrastructure.Models.Request;

public interface IBedrockRequest
{
    [JsonPropertyName("messageVersion")] string MessageVersion { get; set; }

    [JsonPropertyName("agent")] Agent Agent { get; set; }

    [JsonPropertyName("inputText")] string InputText { get; set; }

    [JsonPropertyName("sessionId")] string SessionId { get; set; }

    [JsonPropertyName("actionGroup")] string ActionGroup { get; set; }

    [JsonPropertyName("parameters")] IReadOnlyList<Parameter> Parameters { get; set; }

    [JsonPropertyName("sessionAttributes")]
    SessionAttributes SessionAttributes { get; set; }

    [JsonPropertyName("promptSessionAttributes")]
    PromptSessionAttributes PromptSessionAttribute { get; set; }
}