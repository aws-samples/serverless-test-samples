using FluentAssertions;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Options;
using ServerlessTestApi.Infrastructure;

namespace ApiTests.UnitTest;

public class DynamoDbOptionsTest
{
    [Fact]
    public void DynamoDbOptions_ShouldHaveDefaultTableName()
    {
        // arrange
        var services = new ServiceCollection();

        Startup.AddDefaultServices(services);

        using var provider = services.BuildServiceProvider();

        // act
        var options = provider.GetRequiredService<IOptions<DynamoDbOptions>>().Value;

        // assert
        options.ProductTableName.Should().Be("Products");
    }
}
