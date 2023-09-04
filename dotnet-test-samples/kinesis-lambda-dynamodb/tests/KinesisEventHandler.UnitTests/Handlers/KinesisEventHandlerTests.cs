using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;
using Amazon.Lambda.Core;
using Amazon.Lambda.TestUtilities;
using FakeItEasy;
using FluentAssertions;
using KinesisEventHandler.Handlers;
using KinesisEventHandler.Models;
using KinesisEventHandler.UnitTests.Utilities;
using Xunit;

namespace KinesisEventHandler.UnitTests.Handlers;

public class KinesisEventHandlerTests
{
    private KinesisEventHandler<Employee> InitializeMockKinesisEventHandler()
    {
        var fakeKinesisEventHandler = A.Fake<KinesisEventHandler<Employee>>();

        A.CallTo(() => 
                fakeKinesisEventHandler.ProcessKinesisRecord(A<Employee>._, A<ILambdaContext>._))
            .Returns(Task.CompletedTask);
        
        A.CallTo(() => fakeKinesisEventHandler.ValidateKinesisRecord(A<Employee>._))
            .Returns(Task.FromResult(true));

        return fakeKinesisEventHandler;
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
        var result = await mockKinesisEventTrigger.Handler(kinesisEvent, lambdaContext);

        //Assert
        result.BatchItemFailures.Should().BeEmpty();
        A.CallTo(() => mockKinesisEventTrigger.ProcessKinesisRecord(
            A<Employee>.That.Matches(employee => employee.Equals(expected)),
            A<ILambdaContext>._)).MustHaveHappened();
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
        var result = await mockKinesisEventTrigger.Handler(kinesisEvent, lambdaContext);

        //Assert
        result.BatchItemFailures.Should().BeEmpty();
        A.CallTo(() => 
                mockKinesisEventTrigger.ProcessKinesisRecord(A<Employee>._, A<ILambdaContext>._))
            .MustHaveHappened(employees.Count, Times.Exactly);
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
        await mockKinesisEventTrigger.Handler(kinesisEvent, lambdaContext);

        //Assert
        A.CallTo(() => 
            mockKinesisEventTrigger.ProcessKinesisRecord(
                    A<Employee>._, A<ILambdaContext>._))
            .MustNotHaveHappened();
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
        A.CallTo(() => mockKinesisEventTrigger.ValidateKinesisRecord(
                A<Employee>.That.Matches(e => invalidEmployees.Contains(e))))
            .Throws<ValidationException>();
        
        A.CallTo(() => mockKinesisEventTrigger.ValidateKinesisRecord(
                A<Employee>.That.Matches(e => validEmployees.Contains(e))))
           .Returns(Task.FromResult(true));

        //Act
        var result = await mockKinesisEventTrigger.Handler(kinesisEvent, lambdaContext);

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