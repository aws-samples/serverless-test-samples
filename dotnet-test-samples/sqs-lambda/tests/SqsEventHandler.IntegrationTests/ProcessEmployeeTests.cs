using System.Net;
using Amazon.SQS;
using FluentAssertions;
using SqsEventHandler.IntegrationTests.Utilities;
using Xunit;
using JsonSerializer = System.Text.Json.JsonSerializer;

namespace SqsEventHandler.IntegrationTests;

public class ProcessEmployeeTests : IClassFixture<Setup>, IDisposable
{
    private readonly Setup _setup;
    private readonly AmazonSQSClient _client;
    private bool _disposed;

    public ProcessEmployeeTests(Setup setup)
    {
        _setup = setup;

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

    [Fact]
    public async Task PublishToProcessEmployeeQueue_Should_ReturnSuccess()
    {
        //Arrange
        var sqsMessage = new EmployeeBuilder().Build();

        //Act
        var response = await _setup.SendMessage(
            _client,
            _setup.SqsEventQueueUrl,
            JsonSerializer.Serialize(sqsMessage)
        );

        //Assert
        response.Should().NotBeNull();
        response.HttpStatusCode.Should().Be(HttpStatusCode.OK);
    }
}