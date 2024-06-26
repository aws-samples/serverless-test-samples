using System.Text.Json.Serialization;

namespace ChatbotDemo.Repositories.Mappers;

[JsonConverter(typeof(JsonStringEnumConverter))]
public enum UpsertResult
{
    Inserted,
    Updated,
}