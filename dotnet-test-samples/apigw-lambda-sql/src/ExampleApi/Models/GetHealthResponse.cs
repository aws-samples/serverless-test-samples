using System.Text.Json.Serialization;

namespace ExampleApi.Models;

public class GetHealthResponse
{
    [JsonPropertyName("aws_request_id")] 
    public string AwsRequestId { get; set; }

    [JsonPropertyName("function_name")] 
    public string FunctionName { get; init; }

    [JsonPropertyName("function_version")] 
    public string FunctionVersion { get; init; }
}