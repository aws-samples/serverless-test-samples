using System.Net;
using System.Text.Json;
using FluentAssertions;
using ServerlessTestSamples.IntegrationTest.Drivers;

namespace ServerlessTestSamples.IntegrationTest;

public class IntegrationTest : IClassFixture<Setup>
{
    private HttpClient _httpClient;

    public IntegrationTest()
    {
        _httpClient = new HttpClient();
        _httpClient.DefaultRequestHeaders.Add("INTEGRATION_TEST", "true");
    }

    [Fact]
    public async Task ListStorageAreas_ShouldReturnSuccess()
    {
        var result = await _httpClient.GetAsync($"{Setup.ApiUrl}storage");

        result.StatusCode.Should().Be(HttpStatusCode.OK);

        var responseBody = await result.Content.ReadAsStringAsync();

        var storageAreasResult = JsonSerializer.Deserialize<ListStorageAreasResult>(responseBody);

        storageAreasResult.Should().NotBeNull();
        storageAreasResult.StorageAreas.Should().NotBeNull();
        storageAreasResult.IsSuccess.Should().BeTrue();
    }
}