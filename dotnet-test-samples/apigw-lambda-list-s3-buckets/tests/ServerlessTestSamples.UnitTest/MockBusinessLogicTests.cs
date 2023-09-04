using FakeItEasy;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using ServerlessTestSamples.Core.Queries;
using ServerlessTestSamples.Core.Services;

namespace ServerlessTestSamples.UnitTest;

public class MockBusinessLogicTests
{
    private ILogger<ListStorageAreasQueryHandler> Logger { get; } = A.Fake<ILogger<ListStorageAreasQueryHandler>>();

    [Fact]
    public async Task TestCoreBusinessLogic_With_SuccessfulResponse_Should_ReturnStorageAreas()
    {
        // arrange
        var fakeStorageService = A.Fake<IStorageService>();

        A.CallTo(() => fakeStorageService.ListStorageAreas(A<string>._, A<CancellationToken>._))
            .Returns(Task.FromResult(new ListStorageAreasResult(
                   new List<string>()
                   {
                       "bucket1",
                       "bucket2",
                       "bucket3",
                   })));

        var handler = new ListStorageAreasQueryHandler(fakeStorageService, Logger);

        // act
        var result = await handler.Handle(new() { FilterPrefix = string.Empty }, default);

        // assert
        result.Should().BeEquivalentTo(new ListStorageAreasQueryResult(new[] { "bucket1", "bucket2", "bucket3" }));
    }

    [Fact]
    public async Task TestCoreBusinessLogic_With_ErrorStorageResponse_Should_ReturnEmptyList()
    {
        // arrange
        var fakeStorageService = A.Fake<IStorageService>();

        A.CallTo(() => fakeStorageService.ListStorageAreas(A<string>._, A<CancellationToken>._))
               .Returns(
                   Task.FromResult(
                       new ListStorageAreasResult(Enumerable.Empty<string>(), 
                           false, "Failure retrieving storage data")));

        var handler = new ListStorageAreasQueryHandler(fakeStorageService, Logger);

        // act
        var result = await handler.Handle(new() { FilterPrefix = string.Empty }, default);

        // assert
        result.Should().BeEquivalentTo(new ListStorageAreasQueryResult(Enumerable.Empty<string>()));
    }

    [Fact]
    public async Task TestCoreBusinessLogic_With_StorageServiceException_Should_ReturnEmptyList()
    {
        // arrange
        var fakeStorageService = A.Fake<IStorageService>();

        A.CallTo(() => 
        fakeStorageService.ListStorageAreas(A<string>._, A<CancellationToken>._))
               .Throws<Exception>();

        var handler = new ListStorageAreasQueryHandler(fakeStorageService, Logger);

        // act
        var result = await handler.Handle(new() { FilterPrefix = string.Empty }, default);

        // assert
        result.Should().BeEquivalentTo(new ListStorageAreasQueryResult(Enumerable.Empty<string>()));
    }
}