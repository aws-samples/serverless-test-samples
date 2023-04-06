using System.Net;
using Amazon.SQS;
using FluentAssertions;
using Xunit;
using SqsEventHandler.Models;
using JsonSerializer = System.Text.Json.JsonSerializer;

namespace SqsEventHandler.IntegrationTests;

public class IntegrationTest : IClassFixture<Setup>, IDisposable
{
    private readonly Setup _setup;
    private readonly AmazonSQSClient _client;
    private bool _disposed;

    public IntegrationTest(Setup setup)
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
    public async Task Publish_SQS_Message_Should_Not_Throw_Exception()
    {
        //Arrange
        var sqsMessage = new Employee
        {
            EmployeeId = "IntTest001",
            FirstName = "Integration",
            LastName = "Test",
            Email = "dotnet.integration@test.com",
            DateOfBirth = new DateTime(1990, 11, 05),
            DateOfHire = new DateTime(2007, 11, 05)
        };

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