using System.Text.Json;
using Amazon.Lambda.TestUtilities;
using Amazon.XRay.Recorder.Core;
using FluentAssertions;
using DeleteProduct;
using Microsoft.Extensions.Logging;
using Moq;
using ServerlessTestApi.Core.DataAccess;
using ServerlessTestApi.Core.Models;

namespace ApiTests.UnitTest;

public class MockDeleteProductFunctionTests
{
    private bool _runningLocally = string.IsNullOrEmpty(System.Environment.GetEnvironmentVariable("LOCAL_RUN")) ? true : bool.Parse(System.Environment.GetEnvironmentVariable("LOCAL_RUN"));
    private Mock<ILogger<Function>> _mockLogger = new Mock<ILogger<Function>>();

    public MockDeleteProductFunctionTests()
    {
        // Required for the XRay tracing sub-segment code in the Lambda function handler.
        AWSXRayRecorder.InitializeInstance();    
        AWSXRayRecorder.Instance.BeginSegment("UnitTests");
    }
    
    [Fact]
    public async Task DeleteProduct_ShouldReturnSuccess()
    {
        var apiRequest = new ApiRequestBuilder()
            .WithPathParameter("id", "123456")
            .WithHttpMethod("DELETE")
            .Build();
        
        var mockDataAccessLayer = new Mock<IProductsDAO>();
        mockDataAccessLayer.Setup(p => p.DeleteProduct(It.IsAny<string>())).Verifiable();
        mockDataAccessLayer.Setup(p => p.GetProduct(It.IsAny<string>())).ReturnsAsync(new ProductDTO("123456", "Test Product", 10)).Verifiable();
        
        var function = new Function(mockDataAccessLayer.Object, _mockLogger.Object);

        var result = await function.FunctionHandler(apiRequest, new TestLambdaContext());

        result.StatusCode.Should().Be(200);
        mockDataAccessLayer.Verify(p => p.DeleteProduct(It.IsAny<string>()), Times.Once);
    }
    
    [Theory]
    [InlineData("POST")]
    [InlineData("PUT")]
    [InlineData("GET")]
    public async Task TestLambdaHandler_ForNonDeleteRequests_ShouldReturn405(string httpMethod)
    {
        var apiRequest = new ApiRequestBuilder()
            .WithPathParameter("id", "123456")
            .WithHttpMethod(httpMethod)
            .Build();
        
        var mockDataAccessLayer = new Mock<IProductsDAO>();
        mockDataAccessLayer.Setup(p => p.DeleteProduct(It.IsAny<string>())).Verifiable();
        mockDataAccessLayer.Setup(p => p.GetProduct(It.IsAny<string>())).ReturnsAsync(new ProductDTO("123456", "Test Product", 10)).Verifiable();
        
        var function = new Function(mockDataAccessLayer.Object, _mockLogger.Object);

        var result = await function.FunctionHandler(apiRequest, new TestLambdaContext());

        result.StatusCode.Should().Be(405);
    }
    
    [Fact]
    public async Task DeleteProduct_ErrorInDeleteDataAccess_ShouldReturn500()
    {
        var apiRequest = new ApiRequestBuilder()
            .WithPathParameter("id", "123456")
            .WithHttpMethod("DELETE")
            .Build();
        
        var mockDataAccessLayer = new Mock<IProductsDAO>();
        mockDataAccessLayer.Setup(p => p.DeleteProduct(It.IsAny<string>()))
            .ThrowsAsync(new NullReferenceException());
        mockDataAccessLayer.Setup(p => p.GetProduct(It.IsAny<string>())).ReturnsAsync(new ProductDTO("123456", "Test Product", 10)).Verifiable();
        
        var function = new Function(mockDataAccessLayer.Object, _mockLogger.Object);

        var result = await function.FunctionHandler(apiRequest, new TestLambdaContext());

        result.StatusCode.Should().Be(500);
    }
    
    [Fact]
    public async Task DeleteProduct_ErrorInGet_ShouldReturn500()
    {
        var apiRequest = new ApiRequestBuilder()
            .WithPathParameter("id", "123456")
            .WithHttpMethod("DELETE")
            .Build();
        
        var mockDataAccessLayer = new Mock<IProductsDAO>();
        mockDataAccessLayer.Setup(p => p.DeleteProduct(It.IsAny<string>()))
            .ThrowsAsync(new NullReferenceException());
        mockDataAccessLayer.Setup(p => p.GetProduct(It.IsAny<string>())).ThrowsAsync(new NullReferenceException());
        
        var function = new Function(mockDataAccessLayer.Object, _mockLogger.Object);

        var result = await function.FunctionHandler(apiRequest, new TestLambdaContext());

        result.StatusCode.Should().Be(500);
    }
    
    [Fact]
    public async Task DeleteProduct_ProductNotFound_ShouldReturn400()
    {
        var apiRequest = new ApiRequestBuilder()
            .WithHttpMethod("DELETE")
            .WithPathParameter("id", "123456")
            .Build();
        
        var mockDataAccessLayer = new Mock<IProductsDAO>();
        mockDataAccessLayer.Setup(p => p.DeleteProduct(It.IsAny<string>())).Verifiable();
        mockDataAccessLayer.Setup(p => p.GetProduct(It.IsAny<string>())).ReturnsAsync(() => null).Verifiable();
        
        var function = new Function(mockDataAccessLayer.Object, _mockLogger.Object);

        var result = await function.FunctionHandler(apiRequest, new TestLambdaContext());

        result.StatusCode.Should().Be(400);
        mockDataAccessLayer.Verify(p => p.DeleteProduct(It.IsAny<string>()), Times.Never);
    }
}