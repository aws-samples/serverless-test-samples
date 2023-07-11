using Amazon.Lambda.S3Events;

namespace S3Notificatrions.TestUtilities.Builders;

public class S3EntityBuilder
{
    private S3Event.S3BucketEntity _bucket = new S3BucketEntityBuilder().Build();
    private string _configurationId = "configuration-1";
    private S3Event.S3ObjectEntity _object = new S3ObjectEntityBuilder().Build();
    private string _s3SchemaVersion = "1.2.3.4";

    public S3Event.S3Entity Build()
    {
        return new S3Event.S3Entity
        {
            Bucket = _bucket,
            ConfigurationId = _configurationId,
            Object = _object,
            S3SchemaVersion = _s3SchemaVersion
        };
    }

    public S3EntityBuilder Bucket(S3Event.S3BucketEntity bucket)
    {
        _bucket = bucket;

        return this;
    } 
    
    public S3EntityBuilder ConfigurationId(string configurationId)
    {
        _configurationId = configurationId;

        return this;
    }

    public S3EntityBuilder Object(S3Event.S3ObjectEntity obj)
    {
        _object = obj;

        return this;
    }

    public S3EntityBuilder S3SchemaVersion(string s3SchemaVersion)
    {
        _s3SchemaVersion = s3SchemaVersion;

        return this;
    }
}