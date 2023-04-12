using System.Net;
using Amazon.SQS;
using FluentAssertions;
using SqsEventHandler.IntegrationTests.Utilities;
using xRetry;
using Xunit;
using Xunit.Abstractions;
using JsonSerializer = System.Text.Json.JsonSerializer;

namespace SqsEventHandler.IntegrationTests;

[TestCaseOrderer(
    ordererTypeName: "SqsEventHandler.IntegrationTests.Utilities.PriorityOrderer",
    ordererAssemblyName: "SqsEventHandler.IntegrationTests")]
public class ProcessEmployeeTests : IClassFixture<Setup>, IDisposable
{
    private readonly Setup _setup;
    private readonly ITestOutputHelper _testOutputHelper;
    private readonly AmazonSQSClient _client;
    private const string EmployeeId = "569c13fc-1435-45cb-847d-38e89a86e5a0";
    private bool _disposed;

    public ProcessEmployeeTests(Setup setup, ITestOutputHelper testOutputHelper)
    {
        _setup = setup;
        _testOutputHelper = testOutputHelper;

        // Create the Amazon SQS client
        _client = new AmazonSQSClient();
    }

    public void Dispose()
    {
        if (_disposed)
        {
            return;
        }

        _disposed = true;
        _client.Dispose();
    }

    [Fact, TestPriority(1)]
    public async Task PublishToProcessEmployeeQueue_Should_ReturnSuccess()
    {
        //Arrange
        var sqsMessage = new EmployeeBuilder().WithEmployeeId(EmployeeId);

        //Act
        var response = await _setup.SendMessageAsync(
            _client,
            _setup.SqsEventQueueUrl,
            JsonSerializer.Serialize(sqsMessage)
        );

        //Assert
        response.Should().NotBeNull();
        response.HttpStatusCode.Should().Be(HttpStatusCode.OK);
    }

    [RetryFact(3, 5000), TestPriority(2)]
    public async Task PublishToProcessEmployeeQueue_Should_UpsertEmployee()
    {
        //Act
        //Thread.Sleep(10000);
        using var cts = new CancellationTokenSource();
        var response = await _setup.TestEmployeeRepository!.GetItemAsync(EmployeeId, cts.Token);

        //Assert
        response.Should().NotBeNull();
        response!.EmployeeId.Should().Be(EmployeeId);
        _testOutputHelper.WriteLine(response.ToString());

        //Dispose
        _setup.CreatedEmployeeIds.Add(EmployeeId);
    }
}