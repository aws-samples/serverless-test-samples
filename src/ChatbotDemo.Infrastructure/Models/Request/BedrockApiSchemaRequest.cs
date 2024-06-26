using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace ChatbotDemo.Infrastructure.Models.Request;

public class BedrockApiSchemaRequest : IBedrockRequest
{
    [JsonPropertyName("apiPath")] internal string ApiPath { get; set; }

    [JsonPropertyName("httpMethod")] internal string HttpMethod { get; set; }

    [JsonPropertyName("requestBody")] RequestBody RequestBody { get; set; }

    [JsonPropertyName("messageVersion")] public string MessageVersion { get; set; }
    [JsonPropertyName("agent")] public Agent Agent { get; set; }
    [JsonPropertyName("inputText")] public string InputText { get; set; }
    [JsonPropertyName("sessionId")] public string SessionId { get; set; }
    [JsonPropertyName("actionGroup")] public string ActionGroup { get; set; }
    [JsonPropertyName("parameters")] public IReadOnlyList<Parameter> Parameters { get; set; }

    [JsonPropertyName("sessionAttributes")]
    public SessionAttributes SessionAttributes { get; set; }

    [JsonPropertyName("promptSessionAttribute")]
    public PromptSessionAttributes PromptSessionAttribute { get; set; }
}