using System;
using System.Threading;
using System.Threading.Tasks;
using Amazon.Lambda.TestUtilities;
using Amazon.Runtime.SharedInterfaces;
using FluentAssertions;
using FakeItEasy;
using SqsEventHandler.Functions;
using SqsEventHandler.Repositories;
using SqsEventHandler.Repositories.Mappers;
using SqsEventHandler.Repositories.Models;
using SqsEventHandler.UnitTests.Utilities;
using Xunit;

namespace SqsEventHandler.UnitTests.Functions;

public class ProcessEmployeeFunctionTests
{
    [Fact]
    public Task ProcessEmployeeFunction_Should_ExecuteSuccessfully()
    {
        //Arrange
        var fakeRepository = A.Fake<IDynamoDbRepository<EmployeeDto>>();

        A.CallTo(() => fakeRepository.PutItemAsync(A<EmployeeDto>._, A<CancellationToken>._))
            .Returns(Task.FromResult(UpsertResult.Inserted));

        var sut = new ProcessEmployeeFunction(fakeRepository);
        var employee = new EmployeeBuilder().Build();
        var context = new TestLambdaContext();

        //Act
        var taskResult = sut.ProcessSqsMessage(employee, context);

        //Assert
        Assert.True(taskResult.IsCompleted);
        return Task.CompletedTask;
    }

    [Fact]
    public async Task ProcessEmployeeFunction_Should_NotThrowArgumentNullException()
    {
        //Arrange
        var fakeRepository = A.Fake<IDynamoDbRepository<EmployeeDto>>();

        A.CallTo(() => fakeRepository.PutItemAsync(A<EmployeeDto>._, A<CancellationToken>._))
            .Returns(Task.FromResult(UpsertResult.Inserted));

        var sut = new ProcessEmployeeFunction(fakeRepository);
        var employee = new EmployeeBuilder().Build();
        var context = new TestLambdaContext();

        //Act & Assert
        await sut.Invoking(_ => sut.ProcessSqsMessage(employee, context))
            .Should()
            .NotThrowAsync<ArgumentNullException>();
    }

    [Fact]
    public async Task ProcessEmployeeFunction_Should_ThrowArgumentNullException()
    {
        //Arrange
        var fakeRepository = A.Fake<IDynamoDbRepository<EmployeeDto>>();

        A.CallTo(() => fakeRepository.PutItemAsync(A<EmployeeDto>._, A<CancellationToken>._))
            .Returns(Task.FromResult(UpsertResult.Inserted));

        var sut = new ProcessEmployeeFunction(fakeRepository);
        var employee = new EmployeeBuilder().WithEmployeeId(null);
        var context = new TestLambdaContext();

        //Act & Assert
        await sut.Invoking(_ => sut.ProcessSqsMessage(employee, context))
            .Should()
            .ThrowAsync<ArgumentNullException>()
            .WithMessage("Value cannot be null. (Parameter 'EmployeeId')");
    }
}