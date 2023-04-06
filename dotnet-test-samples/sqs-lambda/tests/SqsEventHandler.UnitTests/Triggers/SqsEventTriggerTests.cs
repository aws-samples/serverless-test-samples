using System;
using System.Collections.Generic;
using System.Text.Json;
using System.Threading.Tasks;
using Amazon.Lambda.Core;
using Amazon.Lambda.SQSEvents;
using Amazon.Lambda.TestUtilities;
using FluentAssertions;
using Moq;
using SqsEventHandler.Handlers;
using SqsEventHandler.Models;
using Xunit;

namespace SqsEventHandler.UnitTests.Triggers;

public class SqsEventTriggerTests
{
    private readonly Mock<SqsEventHandler<Employee>> _mockSqsEventTrigger;

    public SqsEventTriggerTests()
    {
        _mockSqsEventTrigger = new Mock<SqsEventHandler<Employee>>();

        _mockSqsEventTrigger.Setup(x =>
                x.ProcessSqsMessage(It.IsAny<Employee>(), It.IsAny<ILambdaContext>()))
            .Returns(Task.CompletedTask);
    }

    [Fact]
    public async Task SqsEventTrigger_with_One_SQSMessage_Should_Call_ProcessSqsMessage_Once()
    {
        //Arrange
        var expected = new Employee
        {
            EmployeeId = "100",
            DateOfBirth = new DateTime(1990, 11, 05),
            DateOfHire = new DateTime(2007, 11, 05)
        };

        var sqsEvent = new SQSEvent
        {
            Records = new List<SQSEvent.SQSMessage>
            {
                new()
                {
                    MessageId = Guid.NewGuid().ToString(),
                    Body = JsonSerializer.Serialize(expected),
                    EventSource = "aws:sqs"
                }
            }
        };
        var lambdaContext = new TestLambdaContext();

        //Act
        var result = await _mockSqsEventTrigger.Object.Handler(sqsEvent, lambdaContext);

        //Assert
        result.BatchItemFailures.Should().BeEmpty();
        _mockSqsEventTrigger.Verify(x =>
                x.ProcessSqsMessage(
                    It.Is<Employee>(employee => employee.Equals(expected)),
                    It.IsAny<ILambdaContext>()),
            Times.Once);
    }

    [Fact]
    public async Task SqsEventTrigger_with_Two_SQSMessages_Should_Call_ProcessSqsMessage_Twice()
    {
        //Arrange
        var expected1 = new Employee
        {
            EmployeeId = "100",
            DateOfBirth = new DateTime(1990, 11, 05),
            DateOfHire = new DateTime(2007, 11, 05)
        };
        var expected2 = new Employee
        {
            EmployeeId = "101",
            DateOfBirth = new DateTime(1990, 11, 05),
            DateOfHire = new DateTime(2007, 11, 06)
        };

        var sqsEvent = new SQSEvent
        {
            Records = new List<SQSEvent.SQSMessage>
            {
                new()
                {
                    MessageId = Guid.NewGuid().ToString(),
                    Body = JsonSerializer.Serialize(expected1),
                    EventSource = "aws:sqs"
                },
                new()
                {
                    MessageId = Guid.NewGuid().ToString(),
                    Body = JsonSerializer.Serialize(expected2),
                    EventSource = "aws:sqs"
                }
            }
        };
        var lambdaContext = new TestLambdaContext();

        //Act
        var result = await _mockSqsEventTrigger.Object.Handler(sqsEvent, lambdaContext);

        //Assert
        result.BatchItemFailures.Should().BeEmpty();
        _mockSqsEventTrigger.Verify(x =>
                x.ProcessSqsMessage(
                    It.Is<Employee>(employee => employee.Equals(expected1)),
                    It.IsAny<ILambdaContext>()),
            Times.Once);
        _mockSqsEventTrigger.Verify(x =>
                x.ProcessSqsMessage(
                    It.Is<Employee>(employee => employee.Equals(expected2)),
                    It.IsAny<ILambdaContext>()),
            Times.Once);
    }

    [Fact]
    public async Task SqsEventTrigger_with_Zero_SQSMessages_Should_Return_BatchItemFailures()
    {
        //Arrange
        var sqsEvent = new SQSEvent
        {
            Records = new List<SQSEvent.SQSMessage>
            {
                new()
                {
                    MessageId = Guid.NewGuid().ToString(),
                    Body = null,
                    EventSource = "aws:sqs"
                }
            }
        };
        var lambdaContext = new TestLambdaContext();

        //Act
        var result = await _mockSqsEventTrigger.Object.Handler(sqsEvent, lambdaContext);

        //Assert
        result.BatchItemFailures.Should().NotBeEmpty();
        _mockSqsEventTrigger.Verify(x =>
                x.ProcessSqsMessage(
                    It.IsAny<Employee>(),
                    It.IsAny<ILambdaContext>()),
            Times.Never);
    }
}