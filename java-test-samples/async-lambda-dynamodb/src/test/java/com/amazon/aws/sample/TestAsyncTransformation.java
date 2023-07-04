package com.amazon.aws.sample;

import static io.github.resilience4j.core.IntervalFunction.ofExponentialBackoff;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.Callable;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable;

import io.github.resilience4j.core.IntervalFunction;
import io.github.resilience4j.retry.Retry;
import io.github.resilience4j.retry.RetryConfig;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.cloudformation.CloudFormationClient;
import software.amazon.awssdk.services.cloudformation.model.DescribeStacksRequest;
import software.amazon.awssdk.services.cloudformation.model.DescribeStacksResponse;
import software.amazon.awssdk.services.cloudformation.model.Output;
import software.amazon.awssdk.services.cloudformation.model.Stack;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.AttributeValue;
import software.amazon.awssdk.services.dynamodb.model.DynamoDbException;
import software.amazon.awssdk.services.dynamodb.model.GetItemRequest;
import software.amazon.awssdk.services.dynamodb.model.GetItemResponse;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;
import software.amazon.awssdk.services.s3.model.PutObjectResponse;

class RecordNotFoundException extends Exception {

    public RecordNotFoundException(String message) {
        super(message);
    }

}

class InternalErrorException extends Exception {

    public InternalErrorException(String message) {
        super(message);
    }

    public InternalErrorException(String message, Throwable throwable) {
        super(message, throwable);
    }

}

class GetItemCallable implements Callable<String> {

    private DynamoDbClient dynamoDbClient;

    private String tableName;

    private String key;

    public GetItemCallable(DynamoDbClient dynamoDbClient, String tableName, String key) {
        this.dynamoDbClient = dynamoDbClient;
        this.tableName = tableName;
        this.key = key;
    }

    @Override
    public String call() throws Exception {
        Map<String, AttributeValue> keyAttributeValues = new HashMap<>();
        keyAttributeValues.put("id", AttributeValue.builder().s(key).build());

        GetItemRequest getItemRequest = GetItemRequest.builder().tableName(tableName)
                .key(keyAttributeValues).build();

        GetItemResponse getItemResponse;

        try {
            getItemResponse = dynamoDbClient.getItem(getItemRequest);
        } catch (DynamoDbException dynamoDbException) {
            throw new InternalErrorException("Error on get item", dynamoDbException);
        }

        if (!getItemResponse.hasItem()) {
            throw new RecordNotFoundException("Record not found");
        }

        Map<String, AttributeValue> itemAttributeValues = getItemResponse.item();

        if (itemAttributeValues.isEmpty() ||
                !itemAttributeValues.containsKey("content")) {
            throw new InternalErrorException("Error on get item");
        }

        String content = itemAttributeValues.get("content").s();

        return content;
    }

}

@EnabledIfEnvironmentVariable(named = "AWS_SAM_STACK_NAME", matches = ".*")
public class TestAsyncTransformation {

    private static S3Client s3Client;

    private static DynamoDbClient dynamoDbClient;

    private static String sourceBucketName = null;

    private static String destinationBucketName = null;

    private static String recordTransformationTable = null;

    private static final String MESSAGE = "this message was created during an integration test";
    private static final String MESSAGE_TO_UPPER_CASE = MESSAGE.toUpperCase();

    @BeforeAll
    public static void runBeforeAll() {
        s3Client = S3Client.builder()
                .httpClient(ApacheHttpClient.create())
                .build();

        dynamoDbClient = DynamoDbClient.builder().build();

        String awsSamStackName = System.getenv("AWS_SAM_STACK_NAME");

        DescribeStacksRequest describeStacksRequest = DescribeStacksRequest.builder().stackName(awsSamStackName)
                .build();

        CloudFormationClient cloudFormationClient = CloudFormationClient.builder().build();

        DescribeStacksResponse describeStacksResponse = cloudFormationClient.describeStacks(describeStacksRequest);
        assertNotNull(describeStacksResponse, "describeStacksResponse may not be null");
        assertTrue(describeStacksResponse.hasStacks(), "describeStacksResponse may not be empty");

        for (Stack stack : describeStacksResponse.stacks()) {
            for (Output output : stack.outputs()) {
                if ("SourceBucketName".equals(output.outputKey())) {
                    sourceBucketName = output.outputValue();
                } else if ("DestinationBucketName".equals(output.outputKey())) {
                    destinationBucketName = output.outputValue();
                } else if ("RecordTransformationTable".equals(output.outputKey())) {
                    recordTransformationTable = output.outputValue();
                }
            }
        }
        assertNotNull(sourceBucketName, "sourceBucketName may not be null");
        assertNotNull(destinationBucketName, "destinationBucketName may not be null");
    }

    @Test
    public void testAsyncTransformation_when_txt() {
        String key = String.format("%s.txt", UUID.randomUUID().toString());

        PutObjectRequest putObjectRequest = PutObjectRequest.builder().bucket(sourceBucketName)
                .key(key).build();

        PutObjectResponse putObjectResponse = s3Client.putObject(putObjectRequest, RequestBody.fromString(MESSAGE));
        assertNotNull(putObjectResponse, "putObjectResponse may not be null");

        if (recordTransformationTable != null) {
            try {
                Callable<String> callable = getContentFromDynamoDB(recordTransformationTable, key);

                String contentFromRecordTransformationTable = callable.call();

                assertEquals(contentFromRecordTransformationTable, contentFromRecordTransformationTable,
                        String.format("contentFromRecordTransformationTable must be %s instead of %s",
                                MESSAGE_TO_UPPER_CASE, contentFromRecordTransformationTable));
            } catch (Exception exception) {
                fail("An exception occurred and should not have");
            }
        }
    }

    @Test
    public void testAsyncTransformation_when_not_txt() {
        String key = String.format("%s.not_txt", UUID.randomUUID().toString());

        PutObjectRequest putObjectRequest = PutObjectRequest.builder().bucket(sourceBucketName)
                .key(key).build();

        PutObjectResponse putObjectResponse = s3Client.putObject(putObjectRequest, RequestBody.fromString(MESSAGE));
        assertNotNull(putObjectResponse, "putObjectResponse may not be null");

        if (recordTransformationTable != null) {
            try {
                Callable<String> callable = getContentFromDynamoDB(recordTransformationTable, key);

                callable.call();

                fail("It not reach here, an exception should be thrown");
            } catch (Exception exception) {
                assertTrue((exception instanceof RecordNotFoundException), "An exception occured and shoud not have");
            }
        }
    }

    private Callable<String> getContentFromDynamoDB(String tableName, String key)
            throws InternalErrorException, RecordNotFoundException {
        IntervalFunction intervalFunction = ofExponentialBackoff(3000l, 1.5d);

        RetryConfig retryConfig = RetryConfig.custom().maxAttempts(3).intervalFunction(intervalFunction)
                .retryExceptions(RecordNotFoundException.class).build();
        Retry retry = Retry.of("dynamoDbClient.getItem", retryConfig);

        Callable<String> getItemCallable = new GetItemCallable(dynamoDbClient, tableName, key);

        return Retry.decorateCallable(retry, getItemCallable);
    }

}
