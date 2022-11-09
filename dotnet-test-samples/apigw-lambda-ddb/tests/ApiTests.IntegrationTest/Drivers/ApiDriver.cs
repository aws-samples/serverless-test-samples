using System.Net;
using System.Text;
using System.Text.Json;
using FluentAssertions;

namespace ApiTests.IntegrationTest.Drivers
{
    internal class ApiDriver
    {
        private HttpClient _httpClient;

        public ApiDriver()
        {
            _httpClient = new HttpClient();
            _httpClient.DefaultRequestHeaders.Add("INTEGRATION_TEST", "true");
        }

        public async Task<ProductWrapper> GetProducts()
        {
            var result = await _httpClient.GetAsync($"{Setup.ApiUrl}");

            result.StatusCode.Should().Be(HttpStatusCode.OK);

            return JsonSerializer.Deserialize<ProductWrapper>(await result.Content.ReadAsStringAsync());
        }

        public async Task<Product> GetProduct(string id, HttpStatusCode expectedStatusCode = HttpStatusCode.OK)
        {
            var result = await _httpClient.GetAsync($"{Setup.ApiUrl}{id}");

            result.StatusCode.Should().Be(expectedStatusCode);

            if (expectedStatusCode != HttpStatusCode.OK)
            {
                return null;
            }

            return JsonSerializer.Deserialize<Product>(await result.Content.ReadAsStringAsync());
        }

        public async Task<string> CreateProduct(Product product)
        {
            var result = await _httpClient.PutAsync($"{Setup.ApiUrl}{product.Id}", new StringContent(JsonSerializer.Serialize(product), Encoding.UTF8, "application/json"));

            result.StatusCode.Should().Be(HttpStatusCode.Created);

            Setup.CreatedProductIds.Add(product.Id);

            return await result.Content.ReadAsStringAsync();
        }

        public async Task<string> DeleteProduct(string id)
        {
            var result = await _httpClient.DeleteAsync($"{Setup.ApiUrl}{id}");

            result.StatusCode.Should().Be(HttpStatusCode.OK);
            
            Setup.CreatedProductIds.Remove(id);

            return await result.Content.ReadAsStringAsync();
        }
    }
}
