namespace ApiTests.IntegrationTestWithEmulation;

using System.Net;
using System.Text.Json;

using Amazon.Lambda.Annotations.APIGateway;
using Amazon.Lambda.APIGatewayEvents;
using Amazon.Lambda.TestUtilities;

using FakeItEasy;

using FluentAssertions;

using ServerlessTestApi;
using ServerlessTestApi.Core.DataAccess;
using ServerlessTestApi.Core.Models;

[Collection("APITests")]
public class MockGetProductsFunctionTests : FunctionTest<Function>
{
    private readonly TestStartup _startup;

    public MockGetProductsFunctionTests(TestStartup startup)
    {
        this._startup = startup;
    }

    [Fact]
    public async Task GetProducts_Should_ReturnSuccess()
    {
        var function = new Function(this._startup.ProductsDao, this.Logger, this.JsonOptions);

        // act
        var response = await function.GetProducts(new TestLambdaContext());

        // arrange
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var apiGatewayResponse = JsonSerializer.Deserialize<APIGatewayHttpApiV2ProxyResponse>(response.Serialize(new HttpResultSerializationOptions()
        {
            Format = HttpResultSerializationOptions.ProtocolFormat.HttpApi,
            Version = HttpResultSerializationOptions.ProtocolVersion.V2,
        }));

        var body = JsonSerializer.Deserialize<ProductWrapper>(apiGatewayResponse.Body, this.JsonOptions.Value);

        body!.Products.Should().HaveCountGreaterThan(0);
    }

    [Fact]
    public async Task GetProducts_With_DataAccessReturnsProducts_Should_ReturnInBody()
    {
        var testProduct = new Product(
            Guid.NewGuid().ToString(),
            "TestProduct",
            10);

        this._startup.ProductsDao.PutProduct(testProduct, default)
            .GetAwaiter()
            .GetResult();
        var function = new Function(this._startup.ProductsDao, this.Logger, this.JsonOptions);

        // act
        var response = await function.GetProducts(new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        
        var apiGatewayResponse = JsonSerializer.Deserialize<APIGatewayHttpApiV2ProxyResponse>(response.Serialize(new HttpResultSerializationOptions()
        {
            Format = HttpResultSerializationOptions.ProtocolFormat.HttpApi,
            Version = HttpResultSerializationOptions.ProtocolVersion.V2,
        }));

        var body = JsonSerializer.Deserialize<ProductWrapper>(apiGatewayResponse.Body, this.JsonOptions.Value);

        body.Products.FirstOrDefault(p => p.Id == testProduct.Id).Should().NotBeNull();
    }
    
    // Mocks are used in this test to test non-happy paths.
    [Fact]
    public async Task GetProducts_With_ErrorInDataAccess_Should_Return500()
    {
        var fakeProductDao = A.Fake<IProductsDAO>();

        A.CallTo(() => fakeProductDao.GetAllProducts(A<CancellationToken>._))
            .Throws<NullReferenceException>();

        var function = new Function(fakeProductDao, this.Logger, this.JsonOptions);

        // act
        var response = await function.GetProducts(new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(HttpStatusCode.InternalServerError);
    }

    // Mocks are used in this test to test non-happy paths.
    [Fact]
    public async Task GetProducts_With_TimeOut_Should_Return503()
    {
        var fakeProductDao = A.Fake<IProductsDAO>();

        A.CallTo(() => fakeProductDao.GetAllProducts(A<CancellationToken>._))
            .Throws<TaskCanceledException>();

        var function = new Function(fakeProductDao, this.Logger, this.JsonOptions);

        // act
        var response = await function.GetProducts(new TestLambdaContext());

        // assert
        response.StatusCode.Should().Be(HttpStatusCode.ServiceUnavailable);
    }
}