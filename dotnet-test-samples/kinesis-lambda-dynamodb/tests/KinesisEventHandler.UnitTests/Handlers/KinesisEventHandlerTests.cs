using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;
using Amazon.Lambda.Core;
using Amazon.Lambda.TestUtilities;
using FluentAssertions;
using KinesisEventHandler.Handlers;
using KinesisEventHandler.Models;
using KinesisEventHandler.UnitTests.Utilities;
using Moq;
using Xunit;

namespace KinesisEventHandler.UnitTests.Handlers;

public class KinesisEventHandlerTests
{
    private Mock<KinesisEventHandler<Employee>> InitializeMockKinesisEventHandler()
    {
        var mockKinesisEventTrigger = new Mock<KinesisEventHandler<Employee>>(MockBehavior.Strict);

        mockKinesisEventTrigger.Setup(x =>
                x.ProcessKinesisRecord(It.IsAny<Employee>(), It.IsAny<ILambdaContext>()))
            .Returns(Task.CompletedTask);
        mockKinesisEventTrigger.Setup(x =>
                x.ValidateKinesisRecord(It.IsAny<Employee>()))
            .ReturnsAsync(true);

        return mockKinesisEventTrigger;
    }

    [Fact]
    public async Task KinesisEventHandler_With_OneRecord_Should_CallProcessKinesisRecord_Once()
    {
        //Arrange
        var expected = new EmployeeBuilder().Build();
        var kinesisEvent = new KinesisEventBuilder().WithEmployees(new[] { expected });
        var lambdaContext = new TestLambdaContext();

        //Setup
        var mockKinesisEventTrigger = InitializeMockKinesisEventHandler();

        //Act
        var result = await mockKinesisEventTrigger.Object.Handler(kinesisEvent, lambdaContext);

        //Assert
        result.BatchItemFailures.Should().BeEmpty();
        mockKinesisEventTrigger.Verify(x =>
                x.ProcessKinesisRecord(
                    It.Is<Employee>(employee => employee.Equals(expected)),
                    It.IsAny<ILambdaContext>()),
            Times.Once);
    }

    [Fact]
    public async Task KinesisEventHandler_With_10_Records_Should_CallProcessKinesisRecord_10_Times()
    {
        //Arrange
        var employees = new List<Employee>();

        for (var i = 0; i < 10; i++)
        {
            employees.Add(new EmployeeBuilder().Build());
        }

        var kinesisEvent = new KinesisEventBuilder().WithEmployees(employees);
        var lambdaContext = new TestLambdaContext();

        //Setup
        var mockKinesisEventTrigger = InitializeMockKinesisEventHandler();

        //Act
        var result = await mockKinesisEventTrigger.Object.Handler(kinesisEvent, lambdaContext);

        //Assert
        result.BatchItemFailures.Should().BeEmpty();
        mockKinesisEventTrigger.Verify(x =>
                x.ProcessKinesisRecord(
                    It.IsAny<Employee>(),
                    It.IsAny<ILambdaContext>()),
            Times.Exactly(employees.Count));
    }

    [Fact]
    public async Task KinesisEventHandler_With_Zero_Records_Should_Not_CallProcessKinesisRecord()
    {
        //Arrange
        var kinesisEvent = new KinesisEventBuilder().WithoutEmployees();
        var lambdaContext = new TestLambdaContext();

        //Setup
        var mockKinesisEventTrigger = InitializeMockKinesisEventHandler();

        //Act
        await mockKinesisEventTrigger.Object.Handler(kinesisEvent, lambdaContext);

        //Assert
        mockKinesisEventTrigger.Verify(x =>
                x.ProcessKinesisRecord(
                    It.IsAny<Employee>(),
                    It.IsAny<ILambdaContext>()),
            Times.Never);
    }

    [Fact]
    public async Task KinesisEventHandler_With_InvalidRecords_Should_Return_BatchItemFailures()
    {
        //Arrange
        var randomNumber = (new Random()).Next(2, 20);
        var validEmployees = new List<Employee>();
        var invalidEmployees = new List<Employee>();

        //Adding valid Employees
        for (var i = 0; i < randomNumber; i++)
        {
            validEmployees.Add(new EmployeeBuilder().Build());
        }

        //Adding invalid Employees
        for (var i = 0; i < randomNumber; i++)
        {
            invalidEmployees.Add(new EmployeeBuilder().WithEmployeeId(null));
        }

        var employees = new List<Employee>();
        employees.AddRange(validEmployees);
        employees.AddRange(invalidEmployees);
        var kinesisEvent = new KinesisEventBuilder().WithEmployees(employees);
        var lambdaContext = new TestLambdaContext();

        //Setup
        var mockKinesisEventTrigger = InitializeMockKinesisEventHandler();

        //Specific mock for this test
        mockKinesisEventTrigger.Setup(x =>
                x.ValidateKinesisRecord(It.IsIn<Employee>(invalidEmployees)))
            .ThrowsAsync(new ValidationException());
        mockKinesisEventTrigger.Setup(x =>
                x.ValidateKinesisRecord(It.IsIn<Employee>(validEmployees)))
            .ReturnsAsync(true);

        //Act
        var result = await mockKinesisEventTrigger.Object.Handler(kinesisEvent, lambdaContext);

        //Assert
        result.BatchItemFailures.Should().HaveCount(invalidEmployees.Count).And.OnlyHaveUniqueItems();

        result.BatchItemFailures
            .Select(b => b.ItemIdentifier)
            .Should()
            .BeSubsetOf(
                kinesisEvent.Records
                    .Select(k => k.Kinesis.SequenceNumber)
            );
    }
}