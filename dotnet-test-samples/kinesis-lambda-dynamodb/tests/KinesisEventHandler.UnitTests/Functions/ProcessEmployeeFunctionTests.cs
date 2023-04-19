using System;
using System.Threading;
using System.Threading.Tasks;
using Amazon.Lambda.TestUtilities;
using FluentAssertions;
using KinesisEventHandler.Functions;
using KinesisEventHandler.Repositories;
using KinesisEventHandler.Repositories.Mappers;
using KinesisEventHandler.Repositories.Models;
using KinesisEventHandler.UnitTests.Utilities;
using Moq;
using Xunit;

namespace KinesisEventHandler.UnitTests.Functions;

public class ProcessEmployeeFunctionTests
{
    [Fact]
    public Task ProcessEmployeeFunction_Should_ExecuteSuccessfully()
    {
        //Arrange
        var repository = new Mock<IDynamoDbRepository<EmployeeDto>>();

        repository.Setup(x =>
                x.PutItemAsync(It.IsAny<EmployeeDto>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(UpsertResult.Inserted);

        var sut = new ProcessEmployeeFunction(repository.Object);
        var employee = new EmployeeBuilder().Build();
        var context = new TestLambdaContext();

        //Act
        var taskResult = sut.ProcessKinesisRecord(employee, context);

        //Assert
        Assert.True(taskResult.IsCompleted);
        return Task.CompletedTask;
    }

    [Fact]
    public async Task ProcessEmployeeFunction_Should_NotThrowArgumentNullException()
    {
        //Arrange
        var repository = new Mock<IDynamoDbRepository<EmployeeDto>>();

        repository.Setup(x =>
                x.PutItemAsync(It.IsAny<EmployeeDto>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(UpsertResult.Inserted);

        var sut = new ProcessEmployeeFunction(repository.Object);
        var employee = new EmployeeBuilder().Build();
        var context = new TestLambdaContext();

        //Act & Assert
        await sut.Invoking(x => sut.ProcessKinesisRecord(employee, context))
            .Should()
            .NotThrowAsync<ArgumentNullException>();
    }

    [Fact]
    public async Task ProcessEmployeeFunction_Should_ThrowArgumentNullException()
    {
        //Arrange
        var repository = new Mock<IDynamoDbRepository<EmployeeDto>>();

        repository.Setup(x =>
                x.PutItemAsync(It.IsAny<EmployeeDto>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(UpsertResult.Inserted);

        var sut = new ProcessEmployeeFunction(repository.Object);
        var employee = new EmployeeBuilder().WithEmployeeId(null);
        var context = new TestLambdaContext();

        //Act & Assert
        await sut.Invoking(x => sut.ProcessKinesisRecord(employee, context))
            .Should()
            .ThrowAsync<ArgumentNullException>()
            .WithMessage("Value cannot be null. (Parameter 'EmployeeId')");
    }
}