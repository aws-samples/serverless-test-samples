using System.Globalization;
using Amazon.DynamoDBv2.Model;
using KinesisEventHandler.Repositories.Models;

namespace KinesisEventHandler.Repositories.Mappers;

public static class EmployeeMapper
{
    public const string EmployeeId = "employee_id";
    private const string Email = "email";
    private const string FirstName = "first_name";
    private const string LastName = "last_name";
    private const string DateOfBirth = "dob";
    private const string DateOfHire = "doh";

    public static EmployeeDto EmployeeFromDynamoDb(Dictionary<string, AttributeValue> items) =>
        new(
            items[EmployeeId].S,
            items[Email].S,
            items[FirstName].S,
            items[LastName].S,
            DateTime.Parse(items[DateOfBirth].S),
            DateTime.Parse(items[DateOfHire].S)
        );

    public static Dictionary<string, AttributeValue> EmployeeToDynamoDb(EmployeeDto employee) =>
        new(capacity: 6)
        {
            [EmployeeId] = new AttributeValue(employee.EmployeeId),
            [Email] = new AttributeValue(employee.Email),
            [FirstName] = new AttributeValue(employee.FirstName),
            [LastName] = new AttributeValue(employee.LastName),
            [DateOfBirth] = new AttributeValue { S = employee.DateOfBirth.ToString(CultureInfo.InvariantCulture) },
            [DateOfHire] = new AttributeValue { S = employee.DateOfHire.ToString(CultureInfo.InvariantCulture) }
        };
}