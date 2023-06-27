using System.Text.Json.Serialization;

namespace ExampleApi.Repositories.Mappers;

[JsonConverter(typeof(JsonStringEnumConverter))]
public enum UpsertResult
{
    Inserted,
    Updated,
}