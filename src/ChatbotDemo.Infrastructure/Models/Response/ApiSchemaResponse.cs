using System.Text.Json.Serialization;
using ChatbotDemo.Infrastructure.Models.Request;

namespace ChatbotDemo.Infrastructure.Models.Response;

public record ApiSchemaResponse(BedrockApiSchemaRequest request)
{
    [JsonPropertyName("actionGroup")] public string ActionGroup { get; set; } = request.ActionGroup;
    [JsonPropertyName("apiPath")] public string ApiPath { get; private set; } = request.ApiPath;
    [JsonPropertyName("httpMethod")] public string HttpMethod { get; set; } = request.HttpMethod;
    [JsonPropertyName("httpStatusCode")] public int HttpStatusCode { get; set; } = 200;
    [JsonPropertyName("responseBody")] public ResponseBody ResponseBody { get; set; }
}