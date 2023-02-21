using FluentAssertions;
using Microsoft.Extensions.Options;
using ServerlessTestSamples.IntegrationTest.Drivers;
using System.Net;
using System.Net.Http.Json;
using System.Text.Json;

namespace ServerlessTestSamples.IntegrationTest;

public class IntegrationTest : IClassFixture<Setup>, IDisposable
{
    private readonly HttpClient _client;
    private bool disposed;

    public IntegrationTest(Setup setup)
    {
        _client = new HttpClient()
        {
            BaseAddress = new Uri(setup.ApiUrl),
            DefaultRequestHeaders =
            {
                { "INTEGRATION_TEST", "true" },
            },
        };
    }

    private IOptions<JsonSerializerOptions> JsonOptions { get; } =
        Options.Create(new JsonSerializerOptions(JsonSerializerDefaults.Web));

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
    public async Task ListStorageAreas_ShouldReturnSuccess()
    {
        // arrange

        // act
        var response = await _client.GetAsync("storage");

        // assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var result = await response.Content.ReadFromJsonAsync<ListStorageAreasResult>();

        result!.StorageAreas.Should().NotBeNull();
        result.IsSuccess.Should().BeTrue();
    }
}