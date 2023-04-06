using System;
using System.Threading.Tasks;
using Amazon.Lambda.TestUtilities;
using FluentAssertions;
using SqsEventHandler.Models;
using Xunit;

namespace SqsEventHandler.UnitTests;

public class ProcessEmployeeFunctionTests
{
    [Fact]
    public async Task ProcessSqsMessage_with_Valid_SQSMessage_Should_not_Throw_ArgumentNullException()
    {
        //Arrange
        var sut = new ProcessEmployeeFunction();
        var employee = new Employee
        {
            EmployeeId = "100"
        };
        var context = new TestLambdaContext();

        //Act & Assert
        await sut.Invoking(x => sut.ProcessSqsMessage(employee, context))
            .Should()
            .NotThrowAsync<ArgumentNullException>();
    }

    [Fact]
    public async Task ProcessSqsMessage_with_Invalid_SQS_Message_Should_Throw_ArgumentNullException()
    {
        //Arrange
        var sut = new ProcessEmployeeFunction();
        var employee = new Employee
        {
            FirstName = "UnitTest"
        };
        var context = new TestLambdaContext();

        //Act & Assert
        await sut.Invoking(x => sut.ProcessSqsMessage(employee, context))
            .Should()
            .ThrowAsync<ArgumentNullException>()
            .WithMessage("Value cannot be null. (Parameter 'EmployeeId')");
    }
}