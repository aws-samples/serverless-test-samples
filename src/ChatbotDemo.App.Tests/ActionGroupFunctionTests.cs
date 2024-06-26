using Amazon.Lambda.Core;
using ChatbotDemo.App.Functions;
using ChatbotDemo.Infrastructure.Models.Request;
using FluentAssertions;
using NSubstitute;

namespace ChatbotDemo.App.Tests;

public class ActionGroupFunctionTests
{
    [Fact]
    public async Task ProcessBedrockEvent_ShouldReturnExpectedResponse()
    {
        // Arrange
        var request = new BedrockFunctionDetailsRequest();
        var lambdaContext = Substitute.For<ILambdaContext>();
        var sut = new ActionGroupFunction();

        // Act
        var response = await sut.ProcessBedrockEvent(request, lambdaContext);

        // Assert
        response.Should().NotBeNull();
        response.Response.FunctionResponse.ResponseBody.ResponseContentType.Body.Should().Be(
            "Chicken has 20 gm of fat per serving. Shrimp has 30 gm of fat per serving. Beef has 50 gm of fat per serving");
    }

    [Fact]
    public async Task ValidateBedrockEvent_ShouldReturnTrue()
    {
        // Arrange
        var request = new BedrockFunctionDetailsRequest();
        var sut = new ActionGroupFunction();

        // Act
        var isValid = await sut.ValidateBedrockEvent(request);

        // Assert
        isValid.Should().BeTrue();
    }
}