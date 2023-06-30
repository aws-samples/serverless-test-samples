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
            String contentFromRecordTransformationTable = getContentFromDynamoDB(recordTransformationTable, key);
            assertEquals(MESSAGE_TO_UPPER_CASE, contentFromRecordTransformationTable,
                    String.format("contentFromRecordTransformationTable must be %s instead of %s",
                            MESSAGE_TO_UPPER_CASE, contentFromRecordTransformationTable));
        }
    }

    @Test
    // TODO: check the thrown exception when the item is not found
    public void testAsyncTransformation_when_not_txt() {
        String key = String.format("%s.not_txt", UUID.randomUUID().toString());

        PutObjectRequest putObjectRequest = PutObjectRequest.builder().bucket(sourceBucketName)
                .key(key).build();

        PutObjectResponse putObjectResponse = s3Client.putObject(putObjectRequest, RequestBody.fromString(MESSAGE));
        assertNotNull(putObjectResponse, "putObjectResponse may not be null");

        if (recordTransformationTable != null) {
            String contentFromRecordTransformationTable = getContentFromDynamoDB(recordTransformationTable, key);
            assertTrue(contentFromRecordTransformationTable == null,
                    String.format("contentFromRecordTransformationTable must be null instead of %s",
                            contentFromRecordTransformationTable));
        }
    }

    // TODO: check about usage of a retry library
    // TODO: throw an exception instead of return null when it is not found
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

            GetItemRequest getItemRequest = GetItemRequest.builder().tableName(recordTransformationTable)
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

            break;
        }

        return content;
    }

}
