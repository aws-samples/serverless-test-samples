using Amazon.Lambda.S3Events;

namespace S3Notificatrions.TestUtilities.Builders;

public class S3ObjectEntityBuilder
{
    private string _etag = "etag-1";
    private string _key = "key-1";
    private string _sequencer = "seq-1";
    private long _size = 123;
    private string _versionId = "1.2.3.4";

    public S3Event.S3ObjectEntity Build()
    {
        return new S3Event.S3ObjectEntity
        {
            ETag = _etag,
            Key = _key,
            Sequencer = _sequencer,
            Size = _size,
            VersionId = _versionId
        };
    }

    public S3ObjectEntityBuilder ETag(string etag)
    {
        _etag = etag;

        return this;
    }   
    
    public S3ObjectEntityBuilder Key(string key)
    {
        _key = key;

        return this;
    }  
    
    public S3ObjectEntityBuilder Squencer(string sequemcer)
    {
        _sequencer = sequemcer;

        return this;
    }  
    
    public S3ObjectEntityBuilder Size(long size)
    {
        _size = size;

        return this;
    }  
    
    public S3ObjectEntityBuilder VersionId(string versionId)
    {
        _versionId = versionId;

        return this;
    }
}