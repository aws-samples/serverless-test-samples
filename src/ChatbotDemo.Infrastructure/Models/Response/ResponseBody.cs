using System.Text.Json.Serialization;

namespace ChatbotDemo.Infrastructure.Models.Response;

public class ResponseBody
{
    [JsonPropertyName("TEXT")]
    public ResponseContentType ResponseContentType { get; set; }
}