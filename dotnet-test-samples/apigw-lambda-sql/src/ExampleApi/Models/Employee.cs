using System;
using System.Text.Json.Serialization;
using ExampleApi.Repositories.Models;

namespace ExampleApi.Models;

public record Employee
{
    [JsonPropertyName("employee_id")] 
    public string EmployeeId { get; set; }

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

    public EmployeeDto AsDto() => new(EmployeeId, Email, FirstName, LastName, DateOfBirth, DateOfHire);
}