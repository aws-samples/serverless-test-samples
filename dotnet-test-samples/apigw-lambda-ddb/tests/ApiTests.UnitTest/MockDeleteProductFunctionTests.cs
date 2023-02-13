using Amazon.Lambda.TestUtilities;
using DeleteProduct;
using FluentAssertions;
using Moq;
using ServerlessTestApi.Core.DataAccess;
using ServerlessTestApi.Core.Models;

namespace ApiTests.UnitTest;

public class MockDeleteProductFunctionTests : FunctionTest<Function>
{   
    [Fact]
    public async Task DeleteProduct_ShouldReturnSuccess()
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithPathParameter("id", "123456")
            .WithHttpMethod(HttpMethod.Delete)
            .Build();
        
        var data = new Mock<IProductsDAO>();

        data.Setup(d => d.GetProduct(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new ProductDTO("123456", "Test Product", 10));
        
        var function = new Function(data.Object, Logger);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(200);
        data.Verify(d => d.DeleteProduct("123456", It.IsAny<CancellationToken>()), Times.Once);
    }
    
    [Theory]
    [InlineData("POST")]
    [InlineData("PUT")]
    [InlineData("GET")]
    public async Task TestLambdaHandler_ForNonDeleteRequests_ShouldReturn405(string httpMethod)
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithPathParameter("id", "123456")
            .WithHttpMethod(httpMethod)
            .Build();
        
        var data = new Mock<IProductsDAO>();
        var function = new Function(data.Object, Logger);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(405);
    }
    
    [Fact]
    public async Task DeleteProduct_ErrorInDeleteDataAccess_ShouldReturn500()
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithPathParameter("id", "123456")
            .WithHttpMethod(HttpMethod.Delete)
            .Build();
        
        var data = new Mock<IProductsDAO>();

        data.Setup(d => d.DeleteProduct(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ThrowsAsync(new NullReferenceException());
        
        var function = new Function(data.Object, Logger);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(500);
    }
    
    [Fact]
    public async Task DeleteProduct_TimeOut_ShouldReturn503()
    {
        // arrange
        var request = new ApiRequestBuilder()
            .WithPathParameter("id", "123456")
            .WithHttpMethod(HttpMethod.Delete)
            .Build();
        
        var data = new Mock<IProductsDAO>();

        data.Setup(d => d.DeleteProduct(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ThrowsAsync(new TaskCanceledException());

        var function = new Function(data.Object, Logger);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(503);
    }
}