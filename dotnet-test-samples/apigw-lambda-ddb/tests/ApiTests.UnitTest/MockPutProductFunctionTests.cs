using Amazon.Lambda.TestUtilities;
using FluentAssertions;
using Moq;
using PutProduct;
using ServerlessTestApi.Core.DataAccess;
using ServerlessTestApi.Core.Models;

namespace ApiTests.UnitTest;

public class MockPutProductFunctionTests : FunctionTest<Function>
{   
    [Fact]
    public async Task PutProduct_WhenInserted_ShouldReturn201()
    {
        // arrange
        var product = default(Product);
        var dto = new ProductDTO("testid", "test product", 10);
        var request = new ApiRequestBuilder()
            .WithHttpMethod(HttpMethod.Put)
            .WithBody(dto)
            .WithPathParameter("id", dto.Id)
            .Build();
        
        var data = new Mock<IProductsDAO>();

        data.Setup(d => d.PutProduct(It.IsAny<Product>(), It.IsAny<CancellationToken>()))
            .Callback((Product p, CancellationToken ct) => product = p)
            .ReturnsAsync(UpsertResult.Inserted);
        
        var function = new Function(data.Object, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(201);
        response.Headers["Location"].Should().Be("https://localhost/dev/testid");
        product.Should().BeEquivalentTo(dto);
    }

    [Fact]
    public async Task PutProduct_WhenUpdated_ShouldReturn200()
    {
        // arrange
        var product = default(Product);
        var dto = new ProductDTO("testid", "test product", 10);
        var request = new ApiRequestBuilder()
            .WithHttpMethod(HttpMethod.Put)
            .WithBody(dto)
            .WithPathParameter("id", dto.Id)
            .Build();

        var data = new Mock<IProductsDAO>();

        data.Setup(d => d.PutProduct(It.IsAny<Product>(), It.IsAny<CancellationToken>()))
            .Callback((Product p, CancellationToken ct) => product = p)
            .ReturnsAsync(UpsertResult.Updated);

        var function = new Function(data.Object, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(200);
        response.Headers.Should().BeNull();
        product.Should().BeEquivalentTo(dto);
    }

    [Fact]
    public async Task PutProduct_WithEmptyBody_ShouldReturnBadRequest()
    {
        // arrange
        var product = new ProductDTO("testid", "test product", 10);
        var request = new ApiRequestBuilder()
            .WithHttpMethod(HttpMethod.Put)
            .WithPathParameter("id", product.Id)
            .Build();
        
        var data = new Mock<IProductsDAO>();
        var function = new Function(data.Object, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(400);
        data.Verify(d => d.PutProduct(It.IsAny<Product>(), It.IsAny<CancellationToken>()), Times.Never);
    }
        
    [Fact]
    public async Task PutProduct_WithMismatchingIds_ShouldReturnBadRequest()
    {
        // arrange
        var product = new ProductDTO("testid", "test product", 10);
        var request = new ApiRequestBuilder()
            .WithHttpMethod(HttpMethod.Put)
            .WithPathParameter("id", "adifferentid")
            .WithBody(product)
            .Build();
        
        var data = new Mock<IProductsDAO>();
        var function = new Function(data.Object, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(400);
        response.Body.Should().Be("Product ID in the body does not match path parameter");
        data.Verify(d => d.PutProduct(It.IsAny<Product>(), It.IsAny<CancellationToken>()), Times.Never);
    }
    
    [Theory]
    [InlineData("POST")]
    [InlineData("GET")]
    [InlineData("DELETE")]
    public async Task TestLambdaHandler_ForNonPutRequests_ShouldReturn405(string httpMethod)
    {
        // arrange
        var request = new ApiRequestBuilder()
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
    public async Task PutProduct_ErrorInDataAccess_ShouldReturn500()
    {
        // arrange
        var product = new ProductDTO("testid", "test product", 10);
        
        var request = new ApiRequestBuilder()
            .WithHttpMethod(HttpMethod.Put)
            .WithPathParameter("id", product.Id)
            .WithBody(product)
            .Build();
        
        var data = new Mock<IProductsDAO>();

        data.Setup(d => d.PutProduct(It.IsAny<Product>(), It.IsAny<CancellationToken>()))
            .ThrowsAsync(new NullReferenceException());

        var function = new Function(data.Object, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(500);
    }

    [Fact]
    public async Task PutProduct_TimeOut_ShouldReturn503()
    {
        // arrange
        var product = new ProductDTO("testid", "test product", 10);

        var request = new ApiRequestBuilder()
            .WithHttpMethod(HttpMethod.Put)
            .WithPathParameter("id", product.Id)
            .WithBody(product)
            .Build();

        var data = new Mock<IProductsDAO>();

        data.Setup(d => d.PutProduct(It.IsAny<Product>(), It.IsAny<CancellationToken>()))
            .ThrowsAsync(new TaskCanceledException());

        var function = new Function(data.Object, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(503);
    }
}