using System.Threading.Tasks;
using Amazon.Lambda.Core;
using Amazon.Lambda.TestUtilities;
using FakeItEasy;
using FluentAssertions;
using SqsEventHandler.Handlers;
using SqsEventHandler.Models;
using SqsEventHandler.UnitTests.Utilities;
using Xunit;

namespace SqsEventHandler.UnitTests.Handlers;

public class SqsEventHandlerTests
{
    private readonly SqsEventHandler<Employee> _mockSqsEventTrigger;

    public SqsEventHandlerTests()
    {
        _mockSqsEventTrigger = A.Fake<SqsEventHandler<Employee>>();

        A.CallTo(() => _mockSqsEventTrigger.ProcessSqsMessage(A<Employee>._, A<ILambdaContext>._))
            .Returns(Task.CompletedTask);
    }

    [Fact]
    public async Task SqsEventHandler_Should_CallProcessSqsMessageOnce()
    {
        //Arrange
        var expected = new EmployeeBuilder().Build();
        var sqsEvent = new SqsEventBuilder().WithEmployees(new[] { expected });
        var lambdaContext = new TestLambdaContext();

        //Act
        var result = await _mockSqsEventTrigger.Handler(sqsEvent, lambdaContext);

        //Assert
        result.BatchItemFailures.Should().BeEmpty();
        
        A.CallTo(() => _mockSqsEventTrigger.ProcessSqsMessage(
                expected,
                A<ILambdaContext>._))
            .MustHaveHappenedOnceExactly();
    }

    [Fact]
    public async Task SqsEventHandler_Should_CallProcessSqsMessageTwice()
    {
        //Arrange
        var expected1 = new EmployeeBuilder().WithEmployeeId("101");
        var expected2 = new EmployeeBuilder().WithEmployeeId("102");
        var sqsEvent = new SqsEventBuilder().WithEmployees(new[] { expected1, expected2 });
        var lambdaContext = new TestLambdaContext();

        //Act
        var result = await _mockSqsEventTrigger.Handler(sqsEvent, lambdaContext);

        //Assert
        result.BatchItemFailures.Should().BeEmpty();
        
        A.CallTo(() => _mockSqsEventTrigger.ProcessSqsMessage(
                expected1,
                A<ILambdaContext>._))
            .MustHaveHappenedOnceExactly();
        
        A.CallTo(() => _mockSqsEventTrigger.ProcessSqsMessage(
                expected2,
                A<ILambdaContext>._))
            .MustHaveHappenedOnceExactly();
    }

    [Fact]
    public async Task SqsEventHandler_Should_ReturnBatchItemFailures()
    {
        //Arrange
        var sqsEvent = new SqsEventBuilder().WithoutEmployees();
        var lambdaContext = new TestLambdaContext();

        //Act
        await _mockSqsEventTrigger.Handler(sqsEvent, lambdaContext);

        //Assert
        A.CallTo(() => _mockSqsEventTrigger.ProcessSqsMessage(
                A<Employee>._,
                A<ILambdaContext>._))
            .MustNotHaveHappened();
    }
}