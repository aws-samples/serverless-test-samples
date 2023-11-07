using Amazon.Lambda.TestUtilities;
using FakeItEasy;
using FluentAssertions;
using PutProduct;
using ServerlessTestApi.Core.DataAccess;
using ServerlessTestApi.Core.Models;

namespace ApiTests.UnitTest;

using ProductAPI.Tests;

[Collection("APITests")]
public class MockPutProductFunctionTests : FunctionTest<Function>
{
    private readonly TestStartup _startup;

    public MockPutProductFunctionTests(TestStartup startup)
    {
        this._startup = startup;
    }

    [Fact]
    public async Task PutProduct_WithSuccessfulInsert_Should_Return201()
    {
        // arrange
        var dto = new ProductDTO("testcreateid", "test product", 10);
        var request = new ApiRequestBuilder()
            .WithHttpMethod(HttpMethod.Put)
            .WithBody(dto)
            .WithPathParameter("id", dto.Id)
            .Build();
        
        var function = new Function(this._startup.ProductsDao, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        Assert.Multiple(
            () => response.StatusCode.Should().Be(201),
            () => response.Headers["Location"].Should().Be("https://localhost/dev/testcreateid")
        );
    }

    [Fact]
    public async Task PutProduct_WithSuccessfulUpdate_Should_Return200()
    {
        var dto = new ProductDTO("testUpdateId", "test product", 10);
        var request = new ApiRequestBuilder()
            .WithHttpMethod(HttpMethod.Put)
            .WithBody(dto)
            .WithPathParameter("id", dto.Id)
            .Build();
        
        var function = new Function(this._startup.ProductsDao, Logger, JsonOptions);

        // act
        // Run initil request to create the product
        await function.FunctionHandler(request, new TestLambdaContext());
        // Then a second request to run the update
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(200);
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
        
        var function = new Function(this._startup.ProductsDao, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(400);
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
        
        var function = new Function(this._startup.ProductsDao, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(400);
        response.Body.Should().Be("Product ID in the body does not match path parameter");
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
        
        var function = new Function(this._startup.ProductsDao, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(405);
    }
    
    // Mocks are used in this test to test non-happy paths.
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
        
        var fakeProductDao = A.Fake<IProductsDAO>();

        A.CallTo(() => fakeProductDao.PutProduct(A<Product>._, A<CancellationToken>._))
            .ThrowsAsync(new NullReferenceException());

        var function = new Function(fakeProductDao, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(500);
    }

    // Mocks are used in this test to test non-happy paths.
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

        var fakeProductDao = A.Fake<IProductsDAO>();

        A.CallTo(() => fakeProductDao.PutProduct(A<Product>._, A<CancellationToken>._))
            .ThrowsAsync(new TaskCanceledException());

        var function = new Function(fakeProductDao, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(503);
    }
}