namespace S3Notifications;

public record S3NotificationMessage(string BucketName, string ObjectKey, string EventName);
