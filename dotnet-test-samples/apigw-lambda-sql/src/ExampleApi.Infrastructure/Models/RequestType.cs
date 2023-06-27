using System.Text.Json.Serialization;

namespace ExampleApi.Infrastructure.Models;

[JsonConverter(typeof(JsonStringEnumConverter))]
public enum RequestType
{
    Querystring,
    Path,
    Body
}