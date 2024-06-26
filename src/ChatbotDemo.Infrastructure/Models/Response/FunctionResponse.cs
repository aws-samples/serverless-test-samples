using System.Text.Json.Serialization;

namespace ChatbotDemo.Infrastructure.Models.Response;

public record FunctionResponse
{
    [JsonPropertyName("responseState")]
    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public string ResponseState { get; set; } = null;

    [JsonPropertyName("responseBody")] public ResponseBody ResponseBody { get; set; }
}