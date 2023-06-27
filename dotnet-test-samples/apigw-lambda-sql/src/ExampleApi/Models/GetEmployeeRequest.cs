using System.Text.Json.Serialization;

namespace ExampleApi.Models;

public class GetEmployeeRequest
{
    [JsonPropertyName("employee_id")] 
    public string EmployeeId { get; set; }
}