using System.Text.Json.Serialization;
using ExampleApi.Repositories.Mappers;

namespace ExampleApi.Models;

public class PutEmployeeResponse
{
    [JsonPropertyName("employee_id")] 
    public string EmployeeId { get; set; }

    public UpsertResult Result { get; set; }
}