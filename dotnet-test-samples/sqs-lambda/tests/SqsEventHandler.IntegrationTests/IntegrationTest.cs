using System.Net;
using Amazon.SQS;
using FluentAssertions;
using Xunit;
using Newtonsoft.Json;
using SqsEventHandler.Models;
using Xunit.Abstractions;

namespace SqsEventHandler.IntegrationTests;

public class IntegrationTest : IClassFixture<Setup>, IDisposable
{
    private readonly Setup _setup;
    private readonly ITestOutputHelper _testOutputHelper;
    private readonly AmazonSQSClient _client;
    private bool _disposed;

    public IntegrationTest(Setup setup, ITestOutputHelper testOutputHelper)
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

    [Fact]
    public async Task Publish_SQS_Message_Should_Not_Throw_Exception()
    {
        //Arrange
        var sqsMessage = new Employee
        {
            EmployeeId = "IntTest001",
            FirstName = "Integration Test",
            DateOfBirth = new DateTime(1990, 11, 05),
            DateOfHire = new DateTime(2007, 11, 05)
        };

        // act
        var response = await _setup.SendMessage(
            _client,
            _setup.SqsEventQueueUrl,
            JsonConvert.SerializeObject(sqsMessage)
        );

        //Assert
        response.Should().NotBeNull();
        response.HttpStatusCode.Should().Be(HttpStatusCode.OK);
    }
}