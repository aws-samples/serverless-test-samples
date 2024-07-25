using Amazon.Lambda.TestUtilities;
using FakeItEasy;
using FluentAssertions;
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
        
        var fakeProductDao = A.Fake<IProductsDao>();


        A.CallTo(() => fakeProductDao.PutProduct(A<Product>._, A<CancellationToken>._))
            .Invokes(ctx => product = ctx.Arguments.Get<Product>(0))
            .Returns(Task.FromResult(UpsertResult.Inserted));
        
        var function = new Function(fakeProductDao, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        Assert.Multiple(
            () => response.StatusCode.Should().Be(201),
            () => response.Headers["Location"].Should().Be("https://localhost/dev/testid"),
            () => product.Should().BeEquivalentTo(dto)
            );
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

        var fakeProductDao = A.Fake<IProductsDao>();

        A.CallTo(() => fakeProductDao.PutProduct(A<Product>._, A<CancellationToken>._))
            .Invokes(ctx => product = ctx.Arguments.Get<Product>(0))
            .Returns(Task.FromResult(UpsertResult.Updated));

        var function = new Function(fakeProductDao, Logger, JsonOptions);

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
        
        var fakeProductDao = A.Fake<IProductsDao>();
        var function = new Function(fakeProductDao, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(400);
        
        A.CallTo(() => fakeProductDao.PutProduct(A<Product>._, A<CancellationToken>._)).MustNotHaveHappened();
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
        
        var fakeProductDao = A.Fake<IProductsDao>();
        var function = new Function(fakeProductDao, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(400);
        response.Body.Should().Be("Product ID in the body does not match path parameter");
        
        A.CallTo(() => fakeProductDao.PutProduct(A<Product>._, A<CancellationToken>._)).MustNotHaveHappened();
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
        
        var fakeProductDao = A.Fake<IProductsDao>();
        var function = new Function(fakeProductDao, Logger, JsonOptions);

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
        
        var fakeProductDao = A.Fake<IProductsDao>();

        A.CallTo(() => fakeProductDao.PutProduct(A<Product>._, A<CancellationToken>._))
            .ThrowsAsync(new NullReferenceException());

        var function = new Function(fakeProductDao, Logger, JsonOptions);

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

        var fakeProductDao = A.Fake<IProductsDao>();

        A.CallTo(() => fakeProductDao.PutProduct(A<Product>._, A<CancellationToken>._))
            .ThrowsAsync(new TaskCanceledException());

        var function = new Function(fakeProductDao, Logger, JsonOptions);

        // act
        var response = await function.FunctionHandler(request, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(503);
    }
}