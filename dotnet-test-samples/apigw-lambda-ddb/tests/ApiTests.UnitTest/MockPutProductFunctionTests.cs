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
    public async Task PutProduct_WithSuccsfulInsert_Should_Return201()
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
    public async Task PutProduct_WithSuccsfulUpdate_Should_Return200()
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
        product.Should().BeEquivalentTo(dto);
    }

    [Fact]
    public async Task PutProduct_With_EmptyBody_Should_ReturnBadRequest()
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
    public async Task PutProduct_With_MismatchingIds_Should_ReturnBadRequest()
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
    public async Task TestLambdaHandler_With_NonPutRequests_Should_Return405(string httpMethod)
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
    public async Task PutProduct_With_ErrorInDataAccess_Should_Return500()
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
    public async Task PutProduct_With_TimeOut_Should_Return503()
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