using FluentAssertions;
using Microsoft.Extensions.Logging;
using Moq;
using ServerlessTestSamples.Core.Queries;
using ServerlessTestSamples.Core.Services;

namespace ServerlessTestSamples.UnitTest;

public class MockBusinessLogicTests
{
    private ILogger<ListStorageAreasQueryHandler> Logger { get; } = Mock.Of<ILogger<ListStorageAreasQueryHandler>>();

    [Fact]
    public async Task TestCoreBusinessLogic_With_SuccessfulResponse_Should_ReturnStorageAreas()
    {
        // arrange
        var storage = new Mock<IStorageService>();

        storage.Setup(ss => ss.ListStorageAreas(It.IsAny<string>(), It.IsAny<CancellationToken>()))
               .ReturnsAsync(new ListStorageAreasResult(
                   new List<string>()
                   {
                       "bucket1",
                       "bucket2",
                       "bucket3",
                   }));

        var handler = new ListStorageAreasQueryHandler(storage.Object, Logger);

        // act
        var result = await handler.Handle(new() { FilterPrefix = string.Empty }, default);

        // assert
        result.Should().BeEquivalentTo(new ListStorageAreasQueryResult(new[] { "bucket1", "bucket2", "bucket3" }));
    }

    [Fact]
    public async Task TestCoreBusinessLogic_With_ErrorStorageResponse_Should_ReturnEmptyList()
    {
        // arrange
        var storage = new Mock<IStorageService>();

        storage.Setup(p => p.ListStorageAreas(It.IsAny<string>(), It.IsAny<CancellationToken>()))
               .ReturnsAsync(() => new ListStorageAreasResult(Enumerable.Empty<string>(), false, "Failure retrieving storage data"));

        var handler = new ListStorageAreasQueryHandler(storage.Object, Logger);

        // act
        var result = await handler.Handle(new() { FilterPrefix = string.Empty }, default);

        // assert
        result.Should().BeEquivalentTo(new ListStorageAreasQueryResult(Enumerable.Empty<string>()));
    }

    [Fact]
    public async Task TestCoreBusinessLogic_With_StorageServiceException_Should_ReturnEmptyList()
    {
        // arrange
        var storage = new Mock<IStorageService>();

        storage.Setup(p => p.ListStorageAreas(It.IsAny<string>(), It.IsAny<CancellationToken>()))
               .ThrowsAsync(new Exception());

        var handler = new ListStorageAreasQueryHandler(storage.Object, Logger);

        // act
        var result = await handler.Handle(new() { FilterPrefix = string.Empty }, default);

        // assert
        result.Should().BeEquivalentTo(new ListStorageAreasQueryResult(Enumerable.Empty<string>()));
    }
}