using ApiTests.IntegrationTest.Drivers;
using FluentAssertions;
using System.Net;
using System.Net.Http.Json;

namespace ApiTests.IntegrationTest;

public class IntegrationTest : IClassFixture<Setup>, IDisposable
{
    private readonly Setup _setup;
    private readonly HttpClient _client;
    private bool disposed;

    public IntegrationTest(Setup setup)
    {
        _setup = setup;
        _client = new HttpClient()
        {
            BaseAddress = new(setup.ApiUrl),
            DefaultRequestHeaders = { { "INTEGRATION_TEST", "true" } },
        };
    }

    public void Dispose()
    {
        if (disposed)
        {
            return;
        }

        disposed = true;
        _client.Dispose();
    }

    [Fact]
    public async Task CreateProduct_ShouldReturnSuccess()
    {
        // arrange
        var product = new Product(Guid.NewGuid().ToString(), "TestProduct", 10);

        // act
        var response = await _client.PutAsJsonAsync(product.Id, product);

        // assert
        response.StatusCode.Should().Be(HttpStatusCode.Created);
        _setup.CreatedProductIds.Add(product.Id);

        var content = await response.Content.ReadAsStringAsync();

        content.Should().Be($"Created product with id {product.Id}");
        response.Headers.Location.Should().NotBeNull();
    }

    [Fact]
    public async Task RetrieveACreatedProduct_ShouldReturnProduct()
    {
        // arrange
        var id = _setup.CreatedProductIds[0];

        // act
        var response = await _client.GetAsync(id);

        // assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var product = await response.Content.ReadFromJsonAsync<Product>();
        product.Should().BeEquivalentTo(new Product(id, "TestProduct", 10));
    }

    [Fact]
    public async Task GetProducts_ShouldReturnSuccess()
    {
        // arrange
        var id = _setup.CreatedProductIds[0];

        // act
        var response = await _client.GetAsync("/");

        // assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var products = await response.Content.ReadFromJsonAsync<ProductWrapper>();
        products.Should().BeEquivalentTo(new ProductWrapper(new() { new Product(id, "TestProduct", 10) }));
    }

    [Fact]
    public async Task UpdateProduct_CanUpdateProductData_ShouldReturnSuccess()
    {
        // arrange
        var id = _setup.CreatedProductIds[0];
        var expected = new Product(id, "Update name", 20);

        // act
        var response = await _client.PutAsJsonAsync(expected.Id, expected);

        // assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        
        var content = await response.Content.ReadAsStringAsync();
        content.Should().Be($"Updated product with id {expected.Id}");

        response = await _client.GetAsync(id);
        
        var product = await response.EnsureSuccessStatusCode().Content.ReadFromJsonAsync<Product>();
        product.Should().BeEquivalentTo(expected);
    }

    [Fact]
    public async Task DeleteACreatedProduct_ShouldReturnSuccess()
    {
        // arrange
        var id = _setup.CreatedProductIds[0];

        // act
        var response = await _client.DeleteAsync(id);

        // assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var content = await response.Content.ReadAsStringAsync();

        content.Should().Be($"Product with id {id} deleted");
        (await _client.GetAsync(id)).StatusCode.Should().Be(HttpStatusCode.NotFound);
        _setup.CreatedProductIds.Remove(id);
    }
}