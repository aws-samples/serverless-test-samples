using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Amazon.Lambda.Core;
using Amazon.Lambda.SQSEvents;
using Amazon.Lambda.TestUtilities;
using FluentAssertions;
using Moq;
using SqsEventHandler.Models;
using SqsEventHandler.Triggers;
using Xunit;

namespace SqsEventHandler.Tests;

public class SqsEventTriggerTests
{
    private readonly Mock<SqsEventTrigger<Employee>> _mockSqsEventTrigger;

    public SqsEventTriggerTests()
    {
        _mockSqsEventTrigger = new Mock<SqsEventTrigger<Employee>>();

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
                    Body = @"{'employee_id':'100','dob':'11/05/1990','hire_date':'11/05/2007'}",
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
                    Body = @"{'employee_id':'100','dob':'11/05/1990','hire_date':'11/05/2007'}",
                    EventSource = "aws:sqs"
                },
                new()
                {
                    MessageId = Guid.NewGuid().ToString(),
                    Body = @"{'employee_id':'101','dob':'11/05/1990','hire_date':'11/06/2007'}",
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