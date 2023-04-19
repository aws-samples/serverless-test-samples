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
    private readonly Mock<KinesisEventHandler<Employee>> _mockKinesisEventTrigger;

    public KinesisEventHandlerTests()
    {
        _mockKinesisEventTrigger = new Mock<KinesisEventHandler<Employee>>();

        _mockKinesisEventTrigger.Setup(x =>
                x.ProcessKinesisRecord(It.IsAny<Employee>(), It.IsAny<ILambdaContext>()))
            .Returns(Task.CompletedTask);
    }

    [Fact]
    public async Task KinesisEventHandler_Should_CallProcessKinesisRecordOnce()
    {
        //Arrange
        var expected = new EmployeeBuilder().Build();
        var kinesisEvent = new KinesisEventBuilder().WithEmployees(new[] { expected });
        var lambdaContext = new TestLambdaContext();

        //Act
        var result = await _mockKinesisEventTrigger.Object.Handler(kinesisEvent, lambdaContext);

        //Assert
        result.BatchItemFailures.Should().BeEmpty();
        _mockKinesisEventTrigger.Verify(x =>
                x.ProcessKinesisRecord(
                    It.Is<Employee>(employee => employee.Equals(expected)),
                    It.IsAny<ILambdaContext>()),
            Times.Once);
    }

    [Fact]
    public async Task KinesisEventHandler_Should_CallProcessKinesisRecordTwice()
    {
        //Arrange
        var expected1 = new EmployeeBuilder().WithEmployeeId("101");
        var expected2 = new EmployeeBuilder().WithEmployeeId("102");
        var kinesisEvent = new KinesisEventBuilder().WithEmployees(new[] { expected1, expected2 });
        var lambdaContext = new TestLambdaContext();

        //Act
        var result = await _mockKinesisEventTrigger.Object.Handler(kinesisEvent, lambdaContext);

        //Assert
        result.BatchItemFailures.Should().BeEmpty();
        _mockKinesisEventTrigger.Verify(x =>
                x.ProcessKinesisRecord(
                    It.Is<Employee>(employee => employee.Equals(expected1)),
                    It.IsAny<ILambdaContext>()),
            Times.Once);
        _mockKinesisEventTrigger.Verify(x =>
                x.ProcessKinesisRecord(
                    It.Is<Employee>(employee => employee.Equals(expected2)),
                    It.IsAny<ILambdaContext>()),
            Times.Once);
    }

    [Fact]
    public async Task KinesisEventHandler_Should_ReturnBatchItemFailures()
    {
        //Arrange
        var kinesisEvent = new KinesisEventBuilder().WithoutEmployees();
        var lambdaContext = new TestLambdaContext();

        //Act
        var result = await _mockKinesisEventTrigger.Object.Handler(kinesisEvent, lambdaContext);

        //Assert
        result.BatchItemFailures.Should().NotBeEmpty();
        _mockKinesisEventTrigger.Verify(x =>
                x.ProcessKinesisRecord(
                    It.IsAny<Employee>(),
                    It.IsAny<ILambdaContext>()),
            Times.Never);
    }
}