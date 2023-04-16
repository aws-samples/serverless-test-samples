using System.Text.Json.Serialization;

namespace GetStock.Adapters.Model;

internal class CurrencyRates
{
    [JsonPropertyName("base")]
    public string Base { get; set; }

    [JsonPropertyName("date")]
    public string Date { get; set; }

    [JsonPropertyName("rates")]
    public Dictionary<string, double> Rates { get; set; }

    [JsonPropertyName("success")]
    public bool Success { get; set; }

    [JsonPropertyName("timestamp")]
    public int Timestamp { get; set; }
}