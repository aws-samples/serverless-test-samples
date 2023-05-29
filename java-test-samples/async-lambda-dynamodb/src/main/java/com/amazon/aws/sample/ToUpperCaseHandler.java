package com.amazon.aws.sample;

import java.util.HashMap;
import java.util.Map;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.LambdaLogger;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.S3Event;
import com.amazonaws.services.lambda.runtime.events.models.s3.S3EventNotification.S3BucketEntity;
import com.amazonaws.services.lambda.runtime.events.models.s3.S3EventNotification.S3Entity;
import com.amazonaws.services.lambda.runtime.events.models.s3.S3EventNotification.S3EventNotificationRecord;
import com.amazonaws.services.lambda.runtime.events.models.s3.S3EventNotification.S3ObjectEntity;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import software.amazon.awssdk.core.ResponseBytes;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.model.GetObjectResponse;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;

public class ToUpperCaseHandler implements RequestHandler<S3Event, Map<String, Object>> {

    private static S3Client s3Client;

    private static Gson gson;

    private static String destinationBucketName;

    public ToUpperCaseHandler() {
        s3Client = S3Client.builder()
                .httpClient(ApacheHttpClient.create())
                .build();

        gson = new GsonBuilder().setPrettyPrinting().create();

        destinationBucketName = System.getenv("DESTINATION_BUCKET_NAME");
    }

    @Override
    public Map<String, Object> handleRequest(final S3Event s3Event, final Context context) {
        LambdaLogger lambdaLogger = context.getLogger();

        lambdaLogger.log("Started handleResult");
        lambdaLogger.log(String.format("env: %s", gson.toJson(System.getenv())));
        lambdaLogger.log(String.format("context: %s", gson.toJson(context)));
        lambdaLogger.log(String.format("s3Event: %s", gson.toJson(s3Event)));

        Map<String, Object> response = new HashMap<>();

        if (s3Event == null) {
            response.put("success", false);
            response.put("message", "s3Event is null");

            return response;
        }

        for (S3EventNotificationRecord s3EventNotificationRecord : s3Event.getRecords()) {
            S3Entity s3Entity = s3EventNotificationRecord.getS3();
            S3BucketEntity s3BucketEntity = s3Entity.getBucket();
            S3ObjectEntity s3ObjectEntity = s3Entity.getObject();

            GetObjectRequest getObjectRequest = GetObjectRequest.builder().bucket(s3BucketEntity.getName())
                    .key(s3ObjectEntity.getKey()).build();

            ResponseBytes<GetObjectResponse> responseBytes = s3Client.getObjectAsBytes(getObjectRequest);

            String content = responseBytes.asUtf8String();

            if (content == null || content.trim().isEmpty()) {
                lambdaLogger.log("Object's content is null or empty, ignoring it");

                continue;
            }

            lambdaLogger.log(content);

            content = content.toUpperCase();

            lambdaLogger.log(content);

            PutObjectRequest putObjectRequest = PutObjectRequest.builder().bucket(destinationBucketName)
                    .key(s3ObjectEntity.getKey()).build();

            s3Client.putObject(putObjectRequest, RequestBody.fromString(content));
        }

        response.put("success", true);

        lambdaLogger.log("Finished handleResult");

        return response;
    }

}
