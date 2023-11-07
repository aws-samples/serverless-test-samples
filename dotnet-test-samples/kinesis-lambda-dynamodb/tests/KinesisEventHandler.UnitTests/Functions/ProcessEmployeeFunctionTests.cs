using System;
using System.ComponentModel.DataAnnotations;
using System.Threading;
using System.Threading.Tasks;
using Amazon.Lambda.TestUtilities;
using FluentAssertions;
using KinesisEventHandler.Functions;
using KinesisEventHandler.Repositories;
using KinesisEventHandler.Repositories.Mappers;
using KinesisEventHandler.Repositories.Models;
using KinesisEventHandler.UnitTests.Utilities;
using FakeItEasy;
using Xunit;

namespace KinesisEventHandler.UnitTests.Functions;

public class ProcessEmployeeFunctionTests
{
    [Fact]
    public Task ProcessEmployeeFunction_With_ValidEmployeeRecord_Should_ProcessKinesisRecordSuccessfully()
    {
        //Arrange
        var fakeRepository = A.Fake<IDynamoDbRepository<EmployeeDto>>();

        A.CallTo(() => fakeRepository.PutItemAsync(A<EmployeeDto>._, A<CancellationToken>._))
            .Returns(Task.FromResult(UpsertResult.Inserted));

        var sut = new ProcessEmployeeFunction(fakeRepository);
        var employee = new EmployeeBuilder().Build();
        var context = new TestLambdaContext();

        //Act
        var taskResult = sut.ProcessKinesisRecord(employee, context);

        //Assert
        Assert.True(taskResult.IsCompleted);
        return Task.CompletedTask;
    }

    [Fact]
    public async Task ProcessEmployeeFunction_With_ValidEmployeeRecord_Should_PassValidation()
    {
        //Arrange
        var fakeRepository = A.Fake<IDynamoDbRepository<EmployeeDto>>();
        var sut = new ProcessEmployeeFunction(fakeRepository);
        var employee = new EmployeeBuilder().Build();

        //Act
        var result = await sut.ValidateKinesisRecord(employee);

        //Assert
        result.Should().BeTrue();
    }

    [Fact]
    public async Task ProcessEmployeeFunction_With_InvalidEmployeeRecord_Should_ThrowValidationException()
    {
        //Arrange
        var fakeRepository = A.Fake<IDynamoDbRepository<EmployeeDto>>();
        var sut = new ProcessEmployeeFunction(fakeRepository);
        var employee = new EmployeeBuilder().WithEmployeeId(null);

        //Act & Assert
        await sut.Invoking(_ => sut.ValidateKinesisRecord(employee))
            .Should()
            .ThrowAsync<ValidationException>()
            .WithMessage("'EmployeeId' cannot be null or empty");
    }

    [Fact]
    public async Task ProcessEmployeeFunction_With_NullEmployeeRecord_Should_ThrowArgumentNullException()
    {
        //Arrange
        var repository = A.Fake<IDynamoDbRepository<EmployeeDto>>();

        var sut = new ProcessEmployeeFunction(repository);

        //Act & Assert
        await sut.Invoking(_ => sut.ValidateKinesisRecord(null))
            .Should()
            .ThrowAsync<ArgumentNullException>()
            .WithMessage("Value cannot be null. (Parameter 'record')");
    }
}