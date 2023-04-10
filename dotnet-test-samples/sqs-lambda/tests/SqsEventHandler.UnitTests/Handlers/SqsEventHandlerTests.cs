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

namespace SqsEventHandler.UnitTests.Handlers;

public class SqsEventHandlerTests
{
    private readonly Mock<SqsEventHandler<Employee>> _mockSqsEventTrigger;

    public SqsEventHandlerTests()
    {
        _mockSqsEventTrigger = new Mock<SqsEventHandler<Employee>>();

        _mockSqsEventTrigger.Setup(x =>
                x.ProcessSqsMessage(It.IsAny<Employee>(), It.IsAny<ILambdaContext>()))
            .Returns(Task.CompletedTask);
    }

    [Fact]
    public async Task SqsEventTrigger_Should_CallProcessSqsMessageOnce()
    {
        //Arrange
        var expected = new TestEmployeeBuilder().Build();

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
    public async Task SqsEventTrigger_Should_CallProcessSqsMessageTwice()
    {
        //Arrange
        var expected1 = new TestEmployeeBuilder().WithEmployeeId("101");
        var expected2 = new TestEmployeeBuilder().WithEmployeeId("102");

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
    public async Task SqsEventTrigger_Should_ReturnBatchItemFailures()
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