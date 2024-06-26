using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace ChatbotDemo.Infrastructure.Models.Request;

public class Text
{
    [JsonPropertyName("properties")] public IReadOnlyList<Property> Properties { get; set; }
}