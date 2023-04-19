using System.Net;
using FluentAssertions;
using KinesisEventHandler.IntegrationTests.Utilities;
using xRetry;
using Xunit;
using Xunit.Abstractions;

namespace KinesisEventHandler.IntegrationTests;

[TestCaseOrderer(
    ordererTypeName: "KinesisEventHandler.IntegrationTests.Utilities.PriorityOrderer",
    ordererAssemblyName: "KinesisEventHandler.IntegrationTests")]
public class ProcessEmployeeTests : IClassFixture<ProcessEmployeeFixture>, IDisposable
{
    private readonly ProcessEmployeeFixture _processEmployeeFixture;
    private readonly ITestOutputHelper _testOutputHelper;
    private const string EmployeeId = "569c13fc-1435-45cb-847d-38e89a86e5a0";
    private bool _disposed;

    public ProcessEmployeeTests(ProcessEmployeeFixture processEmployeeFixture, ITestOutputHelper testOutputHelper)
    {
        _processEmployeeFixture = processEmployeeFixture;
        _testOutputHelper = testOutputHelper;
    }

    public void Dispose()
    {
        if (_disposed)
        {
            return;
        }

        _disposed = true;
        _processEmployeeFixture.KinesisClient.Dispose();
    }

    [Fact, TestPriority(1)]
    public async Task WriteToEmployeeRecordsStream_Should_ReturnSuccess()
    {
        //Arrange
        var employee = new EmployeeBuilder().WithEmployeeId(EmployeeId);

        //Act
        var response = await _processEmployeeFixture.StreamRecordAsync(employee);

        //Assert
        response.Should().NotBeNull();
        response.HttpStatusCode.Should().Be(HttpStatusCode.OK);
    }

    [RetryFact(3, 5000), TestPriority(2)]
    public async Task WriteToEmployeeRecordsStream_Should_UpsertEmployee()
    {
        //Act
        using var cts = new CancellationTokenSource();
        var response = await _processEmployeeFixture.TestEmployeeRepository!
            .GetItemAsync(EmployeeId, cts.Token);

        //Assert
        response.Should().NotBeNull();
        response!.EmployeeId.Should().Be(EmployeeId);
        _testOutputHelper.WriteLine(response.ToString());

        //Dispose
        _processEmployeeFixture.CreatedEmployeeIds.Add(EmployeeId);
    }
}