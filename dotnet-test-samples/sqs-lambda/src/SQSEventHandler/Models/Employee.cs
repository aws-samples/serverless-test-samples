using System;
using Newtonsoft.Json;

namespace SqsEventHandler.Models;

public record Employee
{
    [JsonProperty("employee_id")] public string EmployeeId { get; set; }

    [JsonProperty("email")] public string Email { get; set; }

    [JsonProperty("first_name")] public string FirstName { get; set; }

    [JsonProperty("last_name")] public string LastName { get; set; }

    [JsonProperty("dob")]
    public DateTime DateOfBirth { get; set; }

    [JsonProperty("hire_date")]
    public DateTime DateOfHire { get; set; }
}