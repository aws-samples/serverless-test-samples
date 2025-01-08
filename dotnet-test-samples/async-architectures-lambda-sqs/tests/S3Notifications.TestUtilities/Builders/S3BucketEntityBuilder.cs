using Amazon.Lambda.S3Events;

namespace S3Notificatrions.TestUtilities.Builders;

public class S3BucketEntityBuilder
{
    private string _arn = "arn-1";
    private string _name = "bucket-name";
    private S3Event.UserIdentityEntity _ownerIdentity = new();

    public S3Event.S3BucketEntity Build()
    {
        return new S3Event.S3BucketEntity
        {
            Arn = _arn,
            Name = _name,
            OwnerIdentity = _ownerIdentity
        };
    }

    public S3BucketEntityBuilder Arn(string arn)
    {
        _arn = arn;

        return this;
    }

    public S3BucketEntityBuilder Name(string name)
    {
        _name = name;

        return this;
    }

    public S3BucketEntityBuilder OwnerIdentity(S3Event.UserIdentityEntity ownerIdentity)

    {
        _ownerIdentity = ownerIdentity;

        return this;
    }
}