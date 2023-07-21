using Amazon.Lambda.TestUtilities;
using FluentAssertions;
using GetProduct;
using Moq;
using ServerlessTestApi.Core.DataAccess;
using ServerlessTestApi.Core.Models;
using System.Text.Json;

namespace ApiTests.UnitTest;

public class MockGetProductFunctionTests : FunctionTest<Function>
{   
    [Fact]
    public async Task GetProduct_ShouldReturnSuccess()
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithPathParameter("id", "123456")
            .WithHttpMethod(HttpMethod.Get)
            .Build();

        var expected = new ProductDTO("testid", "test product", 10);
        var data = new Mock<IProductsDAO>();

        data.Setup(d => d.GetProduct(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(expected);
        
        var function = new Function(data.Object, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(200);

        var body = JsonSerializer.Deserialize<ProductDTO>(response.Body, JsonOptions.Value);

        body.Should().BeEquivalentTo(expected);
    }
    
    [Theory]
    [InlineData("POST")]
    [InlineData("PUT")]
    [InlineData("DELETE")]
    public async Task TestLambdaHandler_ForNonGetRequests_ShouldReturn405(string httpMethod)
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithPathParameter("id", "123456")
            .WithHttpMethod(httpMethod)
            .Build();
        
        var data = new Mock<IProductsDAO>();
        var function = new Function(data.Object, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(405);
    }
    
    [Fact]
    public async Task GetProduct_ErrorInDataAccess_ShouldReturn500()
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithPathParameter("id", "123456")
            .WithHttpMethod(HttpMethod.Get)
            .Build();
        
        var data = new Mock<IProductsDAO>();

        data
            .Setup(d => d.GetProduct(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ThrowsAsync(new NullReferenceException());
        
        var function = new Function(data.Object, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(500);
    }

    [Fact]
    public async Task GetProduct_TimeOut_ShouldReturn503()
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithPathParameter("id", "123456")
            .WithHttpMethod(HttpMethod.Get)
            .Build();

        var data = new Mock<IProductsDAO>();

        data.Setup(d => d.GetProduct(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ThrowsAsync(new TaskCanceledException());

        var function = new Function(data.Object, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(503);
    }

    [Fact]
    public async Task GetProduct_ProductNotFound_ShouldReturn404()
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithHttpMethod(HttpMethod.Get)
            .WithPathParameter("id", "123456")
            .Build();
        
        var data = new Mock<IProductsDAO>();

        data.Setup(d => d.GetProduct(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(() => null);
        
        var function = new Function(data.Object, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(404);
    }
}