using System.Text;
using static Amazon.Lambda.S3Events.S3Event;

namespace S3Notificatrions.TestUtilities.Builders;

public class S3EventNotificationRecordBuilder
{
    private string _awsRegion = "region-1";
    private string _eventName = "event-1";
    private string _eventSource = "event-source-1";
    private DateTime _eventTime = new(2000, 1, 2);
    private string _eventVersion = "1.2.3.4";
    private S3Entity _s3 = new S3EntityBuilder().Build();
    private RequestParametersEntity _requestParameters = new();
    private ResponseElementsEntity _responseElements = new();

    public S3EventNotificationRecord Build()
    {
        return new S3EventNotificationRecord
        {
            AwsRegion = _awsRegion,
            EventName = _eventName,
            EventSource = _eventSource,
            EventTime = _eventTime,
            EventVersion = _eventVersion,
            S3 = _s3,
            RequestParameters = _requestParameters,
            ResponseElements = _responseElements
        };
    }

    public S3EventNotificationRecordBuilder BucketName(string bucketName)
    {
        _s3.Bucket.Name = bucketName;

        return this;
    }
    
    public S3EventNotificationRecordBuilder ObjectKey(string objectKey)
    {
        _s3.Object.Key = objectKey;

        return this;
    }

    public S3EventNotificationRecordBuilder AwsRegion(string awsRegion)
    {
        _awsRegion = awsRegion;

        return this;
    }

    public S3EventNotificationRecordBuilder EventName(string eventName)
    {
        _eventName = eventName;

        return this;
    }

    public S3EventNotificationRecordBuilder EventSource(string eventSource)
    {
        _eventSource = eventSource;

        return this;
    }

    public S3EventNotificationRecordBuilder EventTime(DateTime eventTime)
    {
        _eventTime = eventTime;

        return this;
    }

    public S3EventNotificationRecordBuilder EventVersion(string eventVersion)
    {
        _eventVersion = eventVersion;

        return this;
    }

    public S3EventNotificationRecordBuilder S3(S3Entity s3)
    {
        _s3 = s3;

        return this;
    }

    public S3EventNotificationRecordBuilder RequestParameters(RequestParametersEntity requestParametersEntity)
    {
        _requestParameters = requestParametersEntity;

        return this;
    }

    public S3EventNotificationRecordBuilder ResponseElements(ResponseElementsEntity responseElementsEntity)
    {
        _responseElements = responseElementsEntity;

        return this;
    }
}