using System.Net;
using ApiTests.IntegrationTest.Drivers;
using FluentAssertions;

namespace ApiTests.IntegrationTest;

public class IntegrationTest : IClassFixture<Setup>
{
    private ApiDriver _apiDriver;

    public IntegrationTest()
    {
        _apiDriver = new ApiDriver();
    }

    [Fact]
    public async Task GetProducts_ShouldReturnSuccess()
    {
        var createOrderResult = await _apiDriver.GetProducts();

        createOrderResult.Products.Should().NotBeNull();
    }

    [Fact]
    public async Task CreateProduct_ShouldReturnSuccess()
    {
        var testProductId = Guid.NewGuid().ToString();
        
        var createOrderResult = await _apiDriver.CreateProduct(new Product(testProductId, "TestProduct", 10));

        createOrderResult.Should().Be($"Created product with id {testProductId}");
    }

    [Fact]
    public async Task GetAllProducts_CreatedProductShouldAppearInList()
    {
        var testProductId = Guid.NewGuid().ToString();
        
        var createOrderResult = await _apiDriver.CreateProduct(new Product(testProductId, "TestProduct", 10));

        var allProducts = await this._apiDriver.GetProducts();

        var createdProduct = allProducts.Products.FirstOrDefault(p => p.Id == testProductId);

        createdProduct.Should().NotBeNull();
    }

    [Fact]
    public async Task UpdateProduct_CanUpdateProductData_ShouldReturnSuccess()
    {
        var testProductId = Guid.NewGuid().ToString();
        
        // Initial creation
        await _apiDriver.CreateProduct(new Product(testProductId, "TestProduct", 10));
        
        // Then update the product
        await _apiDriver.CreateProduct(new Product(testProductId, "Update name", 20));

        var product = await _apiDriver.GetProduct(testProductId);

        product.Name.Should().Be("Update name");
        product.Price.Should().Be(20);
    }

    [Fact]
    public async Task RetrieveACreatedProduct_ShouldReturnProduct()
    {
        var testProductId = Guid.NewGuid().ToString();
        
        var createOrderResult = await _apiDriver.CreateProduct(new Product(testProductId, "TestProduct", 10));

        var createdProduct = await _apiDriver.GetProduct(testProductId);

        createdProduct.Should().NotBeNull();
        createdProduct.Name.Should().Be("TestProduct");
    }

    [Fact]
    public async Task DeleteACreatedProduct_ShouldReturnSuccess()
    {
        var testProductId = Guid.NewGuid().ToString();
        
        var createOrderResult = await _apiDriver.CreateProduct(new Product(testProductId, "TestProduct", 10));

        var deleteResult = await _apiDriver.DeleteProduct(testProductId);

        deleteResult.Should().Be($"Product with id {testProductId} deleted");

        var createdProduct = await _apiDriver.GetProduct(testProductId, HttpStatusCode.BadRequest);

        createdProduct.Should().BeNull();
    }
}