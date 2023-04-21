using System.Net;
using FluentAssertions;
using KinesisEventHandler.IntegrationTests.Utilities;
using Xunit;

namespace KinesisEventHandler.IntegrationTests;

public class ProcessEmployeeTests : IClassFixture<ProcessEmployeeFixture>
{
    private readonly ProcessEmployeeFixture _processEmployeeFixture;

    public ProcessEmployeeTests(ProcessEmployeeFixture processEmployeeFixture)
    {
        _processEmployeeFixture = processEmployeeFixture;
    }

    [Fact]
    public async Task WriteToEmployeeRecordsStream_Should_Return_HTTP_OK()
    {
        //Arrange
        var employee = new EmployeeBuilder().Build();

        //Act
        var response = await _processEmployeeFixture.StreamRecordAsync(employee);

        //Assert
        response.Should().NotBeNull();
        response.HttpStatusCode.Should().Be(HttpStatusCode.OK);

        //Dispose
        _processEmployeeFixture.CreatedEmployeeIds.Add(employee.EmployeeId);
    }

    [Fact]
    public async Task WriteToEmployeeRecordsStream_Should_Upsert_To_EmployeeStreamTable()
    {
        //Arrange
        var employee = new EmployeeBuilder().Build();

        //Act
        using var cts = new CancellationTokenSource();
        await _processEmployeeFixture.StreamRecordAsync(employee);
        var response = await _processEmployeeFixture.PollForProcessedMessage(employee, cts.Token);

        //Assert
        response.Should().NotBeNull().And.BeEquivalentTo(employee);

        //Dispose
        _processEmployeeFixture.CreatedEmployeeIds.Add(employee.EmployeeId);
    }
}