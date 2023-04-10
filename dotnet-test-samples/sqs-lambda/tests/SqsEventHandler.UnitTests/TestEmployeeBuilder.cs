using System;
using SqsEventHandler.Models;

namespace SqsEventHandler.UnitTests;

public class TestEmployeeBuilder
{
    private readonly Employee _employee;

    public TestEmployeeBuilder()
    {
        _employee = new Employee
        {
            EmployeeId = "UnitTest001",
            FirstName = "Unit",
            LastName = "Test",
            Email = "dotnet.integration@test.com",
            DateOfBirth = new DateTime(1990, 11, 05),
            DateOfHire = new DateTime(2007, 11, 05)
        };
    }

    public Employee WithEmployeeId(string employeeId)
    {
        _employee.EmployeeId = employeeId;

        return _employee;
    }

    public Employee Build()
    {
        return _employee;
    }
}