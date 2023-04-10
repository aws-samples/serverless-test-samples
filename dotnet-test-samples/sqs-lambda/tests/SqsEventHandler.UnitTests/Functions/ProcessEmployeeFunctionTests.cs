using System;
using System.Threading.Tasks;
using Amazon.Lambda.TestUtilities;
using FluentAssertions;
using SqsEventHandler.Functions;
using SqsEventHandler.UnitTests.Utilities;
using Xunit;

namespace SqsEventHandler.UnitTests.Functions;

public class ProcessEmployeeFunctionTests
{
    [Fact]
    public async Task ProcessEmployeeFunction_Should_NotThrowArgumentNullException()
    {
        //Arrange
        var sut = new ProcessEmployeeFunction();
        var employee = new EmployeeBuilder().Build();
        var context = new TestLambdaContext();

        //Act & Assert
        await sut.Invoking(x => sut.ProcessSqsMessage(employee, context))
            .Should()
            .NotThrowAsync<ArgumentNullException>();
    }

    [Fact]
    public async Task ProcessEmployeeFunction_Should_ThrowArgumentNullException()
    {
        //Arrange
        var sut = new ProcessEmployeeFunction();
        var employee = new EmployeeBuilder().WithEmployeeId(null);
        var context = new TestLambdaContext();

        //Act & Assert
        await sut.Invoking(x => sut.ProcessSqsMessage(employee, context))
            .Should()
            .ThrowAsync<ArgumentNullException>()
            .WithMessage("Value cannot be null. (Parameter 'EmployeeId')");
    }
}