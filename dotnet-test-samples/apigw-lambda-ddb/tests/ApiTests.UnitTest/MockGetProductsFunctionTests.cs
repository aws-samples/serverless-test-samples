using Amazon.Lambda.TestUtilities;
using FluentAssertions;
using GetProducts;
using Moq;
using ServerlessTestApi.Core.DataAccess;
using ServerlessTestApi.Core.Models;
using System.Text.Json;

namespace ApiTests.UnitTest;

public class MockGetProductsFunctionTests : FunctionTest<Function>
{
    [Fact]
    public async Task GetProducts_Should_ReturnSuccess()
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithHttpMethod(HttpMethod.Get)
            .Build();
        var data = new Mock<IProductsDAO>();

        data.Setup(d => d.GetAllProducts(It.IsAny<CancellationToken>())).ReturnsAsync(new ProductWrapper(new()));

        var function = new Function(data.Object, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // arrange
        response.StatusCode.Should().Be(200);

        var body = JsonSerializer.Deserialize<ProductWrapper>(response.Body, JsonOptions.Value);

        body!.Products.Should().HaveCount(0);
    }

    [Fact]
    public async Task GetProducts_With_DataAccessReturnsProducts_Should_ReturnInBody()
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithHttpMethod(HttpMethod.Get)
            .Build();

        var expected = new ProductWrapper(
            new(capacity: 1)
            {
                new("testid", "test product", 10),
            });
        var data = new Mock<IProductsDAO>();

        data.Setup(d => d.GetAllProducts(It.IsAny<CancellationToken>())).ReturnsAsync(expected);

        var function = new Function(data.Object, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(200);

        var body = JsonSerializer.Deserialize<ProductWrapper>(response.Body, JsonOptions.Value);

        body.Should().BeEquivalentTo(expected);
    }

    [Theory]
    [InlineData("POST")]
    [InlineData("PUT")]
    [InlineData("DELETE")]
    public async Task TestLambdaHandler_With_NonGetRequests_Should_Return405(string httpMethod)
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithHttpMethod(httpMethod)
            .Build();

        var data = new Mock<IProductsDAO>();

        data.Setup(d => d.GetAllProducts(It.IsAny<CancellationToken>())).ReturnsAsync(new ProductWrapper(new()));

        var function = new Function(data.Object, Logger, JsonOptions);

        // act
        var result = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        result.StatusCode.Should().Be(405);
    }

    [Fact]
    public async Task GetProducts_With_ErrorInDataAccess_Should_Return500()
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithHttpMethod(HttpMethod.Get)
            .Build();

        var data = new Mock<IProductsDAO>();

        data.Setup(d => d.GetAllProducts(It.IsAny<CancellationToken>()))
            .ThrowsAsync(new NullReferenceException());

        var function = new Function(data.Object, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(500);
    }

    [Fact]
    public async Task GetProducts_With_TimeOut_Should_Return503()
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithHttpMethod(HttpMethod.Get)
            .Build();

        var data = new Mock<IProductsDAO>();

        data.Setup(d => d.GetAllProducts(It.IsAny<CancellationToken>()))
            .ThrowsAsync(new TaskCanceledException());

        var function = new Function(data.Object, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(503);
    }
}