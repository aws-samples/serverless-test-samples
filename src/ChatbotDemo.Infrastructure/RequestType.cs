using System.Text.Json.Serialization;

namespace ChatbotDemo.Infrastructure;

[JsonConverter(typeof(JsonStringEnumConverter))]
public enum RequestType
{
    Querystring,
    Path,
    Body,
    None
}