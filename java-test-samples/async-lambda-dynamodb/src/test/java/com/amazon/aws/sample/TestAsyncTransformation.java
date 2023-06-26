package com.amazon.aws.sample;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable;

import software.amazon.awssdk.core.ResponseBytes;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.cloudformation.CloudFormationClient;
import software.amazon.awssdk.services.cloudformation.model.DescribeStacksRequest;
import software.amazon.awssdk.services.cloudformation.model.DescribeStacksResponse;
import software.amazon.awssdk.services.cloudformation.model.Output;
import software.amazon.awssdk.services.cloudformation.model.Stack;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.AttributeValue;
import software.amazon.awssdk.services.dynamodb.model.DeleteItemRequest;
import software.amazon.awssdk.services.dynamodb.model.DeleteItemResponse;
import software.amazon.awssdk.services.dynamodb.model.DynamoDbException;
import software.amazon.awssdk.services.dynamodb.model.GetItemRequest;
import software.amazon.awssdk.services.dynamodb.model.GetItemResponse;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.DeleteObjectRequest;
import software.amazon.awssdk.services.s3.model.DeleteObjectResponse;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.model.GetObjectResponse;
import software.amazon.awssdk.services.s3.model.NoSuchKeyException;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;
import software.amazon.awssdk.services.s3.model.PutObjectResponse;

@EnabledIfEnvironmentVariable(named = "AWS_SAM_STACK_NAME", matches = ".*")
public class TestAsyncTransformation {

    private static S3Client s3Client;

    private static DynamoDbClient dynamoDbClient;

    private static String sourceBucketName = null;

    private static String destinationBucketName = null;

    private static String recordTrasnformationTable = null;

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
                } else if ("RecordTrasnformationTable".equals(output.outputKey())) {
                    recordTrasnformationTable = output.outputValue();
                }
            }
        }
        assertNotNull(sourceBucketName, "sourceBucketName may not be null");
        assertNotNull(destinationBucketName, "destinationBucketName may not be null");
    }

    @Test
    public void testAsyncTransformation() {
        String key = String.format("%s.txt", UUID.randomUUID().toString());

        PutObjectRequest putObjectRequest = PutObjectRequest.builder().bucket(sourceBucketName)
                .key(key).build();

        PutObjectResponse putObjectResponse = s3Client.putObject(putObjectRequest, RequestBody.fromString(MESSAGE));
        assertNotNull(putObjectResponse, "putObjectResponse may not be null");

        String contentFromDestinationBucketName = getContentFromBucket(destinationBucketName, key);
        assertEquals(MESSAGE_TO_UPPER_CASE, contentFromDestinationBucketName,
                String.format("contentFromDestinationBucketName must be %s instead of %s", MESSAGE_TO_UPPER_CASE,
                        contentFromDestinationBucketName));

        if (recordTrasnformationTable != null) {
            String contentFromRecordTransformationTable = getContentFromDynamoDB(recordTrasnformationTable, key);
            assertEquals(MESSAGE_TO_UPPER_CASE, contentFromRecordTransformationTable,
                    String.format("contentFromRecordTransformationTable must be %s instead of %s",
                            MESSAGE_TO_UPPER_CASE, contentFromRecordTransformationTable));
        }

        DeleteObjectRequest deleteObjectRequest;
        DeleteObjectResponse deleteObjectResponse;

        deleteObjectRequest = DeleteObjectRequest.builder().bucket(sourceBucketName).key(key)
                .build();
        deleteObjectResponse = s3Client.deleteObject(deleteObjectRequest);
        assertNotNull(deleteObjectResponse, "deleteObjectResponse must not be null");

        deleteObjectRequest = DeleteObjectRequest.builder().bucket(destinationBucketName).key(key)
                .build();
        deleteObjectResponse = s3Client.deleteObject(deleteObjectRequest);
        assertNotNull(deleteObjectResponse, "deleteObjectResponse must not be null");

        if (recordTrasnformationTable != null) {
            Map<String, AttributeValue> attributeValues = new HashMap<>();
            attributeValues.put("id", AttributeValue.builder().s(key).build());

            DeleteItemRequest deleteItemRequest = DeleteItemRequest.builder().tableName(recordTrasnformationTable)
                    .key(attributeValues).build();

            DeleteItemResponse deleteItemResponse = dynamoDbClient.deleteItem(deleteItemRequest);
            assertNotNull(deleteItemResponse, "deleteItemResponse may not be null");
        }
    }

    private String getContentFromBucket(String bucket, String key) {
        int numberOfRetries = 0;

        String content = null;

        while (numberOfRetries < 3) {
            try {
                Thread.sleep(5 * 1000);
            } catch (InterruptedException interruptedException) {
                break;
            }

            numberOfRetries++;

            GetObjectRequest getObjectRequest = GetObjectRequest.builder().bucket(bucket)
                    .key(key).build();

            ResponseBytes<GetObjectResponse> responseBytes;

            try {
                responseBytes = s3Client.getObjectAsBytes(getObjectRequest);
            } catch (NoSuchKeyException noSuchKeyException) {
                continue;
            } catch (Exception exception) {
                break;
            }

            content = responseBytes.asUtf8String();
        }

        return content;
    }

    private String getContentFromDynamoDB(String tableName, String key) {
        int numberOfRetries = 0;

        String content = null;

        while (numberOfRetries < 3) {
            try {
                Thread.sleep(5 * 1000);
            } catch (InterruptedException interruptedException) {
                break;
            }

            numberOfRetries++;

            Map<String, AttributeValue> keyAttributeValues = new HashMap<>();
            keyAttributeValues.put("id", AttributeValue.builder().s(key).build());

            GetItemRequest getItemRequest = GetItemRequest.builder().tableName(recordTrasnformationTable)
                    .key(keyAttributeValues).build();

            GetItemResponse getItemResponse;

            try {
                getItemResponse = dynamoDbClient.getItem(getItemRequest);
            } catch (DynamoDbException dynamoDbException) {
                break;
            }

            if (!getItemResponse.hasItem()) {
                continue;
            }

            Map<String, AttributeValue> itemAttributeValues = getItemResponse.item();

            if (itemAttributeValues.isEmpty()) {
                continue;
            }

            content = itemAttributeValues.get("content").s();
        }

        return content;
    }

}
