namespace ApiTests.IntegrationTestWithEmulation;

using System.Net;

using Amazon.Lambda.TestUtilities;

using FakeItEasy;

using FluentAssertions;

using ServerlessTestApi;
using ServerlessTestApi.Core.DataAccess;
using ServerlessTestApi.Core.Models;

[Collection("APITests")]
public class MockGetProductFunctionTests : FunctionTest<Function>
{
    private readonly TestStartup _startup;

    public MockGetProductFunctionTests(TestStartup startup)
    {
        this._startup = startup;
    }

    [Fact]
    public async Task GetProduct_Should_ReturnSuccess()
    {
        var testProduct = new Product(
            Guid.NewGuid().ToString(),
            "TestProduct",
            10);

        this._startup.ProductsDao.PutProduct(testProduct, default)
            .GetAwaiter()
            .GetResult();

        var expected = new ProductDTO(testProduct.Id, testProduct.Name, testProduct.Price);

        var function = new Function(this._startup.ProductsDao, this.Logger, this.JsonOptions);

        // act
        var response = await function.GetProduct(testProduct.Id, new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
    }
    
    [Fact]
    public async Task GetProduct_With_ProductNotFound_Should_Return404()
    {
        var function = new Function(this._startup.ProductsDao, this.Logger, this.JsonOptions);

        // act
        var response = await function.GetProduct("notfound", new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(HttpStatusCode.NotFound);
    }
    
    // Mocks are used in this test to test non-happy paths.
    [Fact]
    public async Task GetProduct_With_ErrorInDataAccess_Should_Return500()
    {
        var fakeProductDao = A.Fake<IProductsDAO>();

        A.CallTo(() => fakeProductDao.GetProduct(A<string>._, A<CancellationToken>._))
            .Throws<NullReferenceException>();
        
        var function = new Function(fakeProductDao, this.Logger, this.JsonOptions);

        // act
        var response = await function.GetProduct("123456", new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(HttpStatusCode.InternalServerError);
    }

    // Mocks are used in this test to test non-happy paths.
    [Fact]
    public async Task GetProduct_With_TimeOut_Should_Return503()
    {
        var fakeProductDao = A.Fake<IProductsDAO>();

        A.CallTo(() => fakeProductDao.GetProduct(A<string>._, A<CancellationToken>._))
            .Throws<TaskCanceledException>();

        var function = new Function(fakeProductDao, this.Logger, this.JsonOptions);

        // act
        var response = await function.GetProduct("123456", new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(HttpStatusCode.ServiceUnavailable);
    }
}