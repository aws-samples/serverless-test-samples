using System.Net;
using Amazon.S3;
using ServerlessTestSamples.Core.Services;

namespace ServerlessTestSamples.Integrations;

public class S3StorageService : IStorageService
{
    private readonly IAmazonS3 _s3Client;

    public S3StorageService(IAmazonS3 client)
    {
        _s3Client = client ?? new AmazonS3Client();
    }

    public async Task<ListStorageAreasResult> ListStorageAreas(string? filterPrefix)
    {
        var buckets = await _s3Client.ListBucketsAsync();

        if (buckets.HttpStatusCode != HttpStatusCode.OK)
        {
            return new ListStorageAreasResult(Enumerable.Empty<string>(), false, "Failure retrieving services from Amazon S3");
        }

        return new ListStorageAreasResult(buckets.Buckets.Select(p => p.BucketName));
    }
}