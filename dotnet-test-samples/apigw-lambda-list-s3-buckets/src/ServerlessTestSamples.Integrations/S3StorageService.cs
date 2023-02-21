using Amazon.S3;
using ServerlessTestSamples.Core.Services;
using System.Net;

namespace ServerlessTestSamples.Integrations;

public class S3StorageService : IStorageService
{
    private readonly IAmazonS3 _client;

    public S3StorageService(IAmazonS3 client) => _client = client;

    public async Task<ListStorageAreasResult> ListStorageAreas(string? filterPrefix, CancellationToken cancellationToken)
    {
        var buckets = await _client.ListBucketsAsync(cancellationToken);

        if (buckets.HttpStatusCode != HttpStatusCode.OK)
        {
            return new(Enumerable.Empty<string>(), false, "Failure retrieving services from Amazon S3");
        }

        return new(buckets.Buckets.Select(p => p.BucketName));
    }
}