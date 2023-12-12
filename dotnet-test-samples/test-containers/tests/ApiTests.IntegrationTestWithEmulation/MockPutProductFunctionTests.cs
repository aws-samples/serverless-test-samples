namespace ApiTests.IntegrationTestWithEmulation;

using System.Net;

using Amazon.Lambda.TestUtilities;

using FakeItEasy;

using FluentAssertions;

using ServerlessTestApi;
using ServerlessTestApi.Core.DataAccess;
using ServerlessTestApi.Core.Models;

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

        var function = new Function(this._startup.ProductsDao, this.Logger, this.JsonOptions);

        // act
        var response = await function.CreateProduct(dto.Id, dto, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(HttpStatusCode.Created);
    }

    [Fact]
    public async Task PutProduct_WithSuccessfulUpdate_Should_Return200()
    {
        var dto = new ProductDTO("testUpdateId", "test product", 10);

        
        var function = new Function(this._startup.ProductsDao, this.Logger, this.JsonOptions);

        // act
        // Run initil request to create the product
        await function.CreateProduct(dto.Id, dto, new TestLambdaContext());
        // Then a second request to run the update
        var response = await function.CreateProduct(dto.Id, dto, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
    }

    [Fact]
    public async Task PutProduct_WithEmptyBody_Should_ReturnBadRequest()
    {
        // arrange
        var product = new ProductDTO("testid", "test product", 10);
        
        var function = new Function(this._startup.ProductsDao, this.Logger, this.JsonOptions);

        // act
        var response = await function.CreateProduct(product.Id, null, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(HttpStatusCode.BadRequest);
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
        
        var function = new Function(this._startup.ProductsDao, this.Logger, this.JsonOptions);

        // act
        var response = await function.CreateProduct("12345", product, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(HttpStatusCode.BadRequest);
    }
    
    // Mocks are used in this test to test non-happy paths.
    [Fact]
    public async Task PutProduct_With_ErrorInDataAccess_Should_Return500()
    {
        // arrange
        var product = new ProductDTO("testid", "test product", 10);
        
        var fakeProductDao = A.Fake<IProductsDAO>();

        A.CallTo(() => fakeProductDao.PutProduct(A<Product>._, A<CancellationToken>._))
            .ThrowsAsync(new NullReferenceException());

        var function = new Function(fakeProductDao, this.Logger, this.JsonOptions);

        // act
        var response = await function.CreateProduct(product.Id, product, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(HttpStatusCode.InternalServerError);
    }

    // Mocks are used in this test to test non-happy paths.
    [Fact]
    public async Task PutProduct_With_TimeOut_Should_Return503()
    {
        // arrange
        var product = new ProductDTO("testid", "test product", 10);

        var fakeProductDao = A.Fake<IProductsDAO>();

        A.CallTo(() => fakeProductDao.PutProduct(A<Product>._, A<CancellationToken>._))
            .ThrowsAsync(new TaskCanceledException());

        var function = new Function(fakeProductDao, this.Logger, this.JsonOptions);

        // act
        var response = await function.CreateProduct(product.Id, product, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(HttpStatusCode.ServiceUnavailable);
    }
}