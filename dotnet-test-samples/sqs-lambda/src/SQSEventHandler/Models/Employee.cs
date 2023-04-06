using System;
using System.Text.Json.Serialization;

namespace SqsEventHandler.Models;

public record Employee
{
    [JsonPropertyName("employee_id")] 
    public string EmployeeId { get; init; }

    [JsonPropertyName("email")] 
    public string Email { get; init; }

    [JsonPropertyName("first_name")] 
    public string FirstName { get; init; }

    [JsonPropertyName("last_name")] 
    public string LastName { get; init; }

    [JsonPropertyName("dob")]
    public DateTime DateOfBirth { get; init; }

    [JsonPropertyName("hire_date")]
    public DateTime DateOfHire { get; init; }
}