package com.amazon.aws.sample;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.UUID;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClient;
import com.amazonaws.services.dynamodbv2.document.DeleteItemOutcome;
import com.amazonaws.services.dynamodbv2.document.DynamoDB;
import com.amazonaws.services.dynamodbv2.document.Item;
import com.amazonaws.services.dynamodbv2.document.Table;

import software.amazon.awssdk.core.ResponseBytes;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.cloudformation.CloudFormationClient;
import software.amazon.awssdk.services.cloudformation.model.DescribeStacksRequest;
import software.amazon.awssdk.services.cloudformation.model.DescribeStacksResponse;
import software.amazon.awssdk.services.cloudformation.model.Output;
import software.amazon.awssdk.services.cloudformation.model.Stack;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.DeleteObjectRequest;
import software.amazon.awssdk.services.s3.model.DeleteObjectResponse;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.model.GetObjectResponse;
import software.amazon.awssdk.services.s3.model.NoSuchKeyException;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;
import software.amazon.awssdk.services.s3.model.PutObjectResponse;

public class TestAsyncTransformation {

    private static S3Client s3Client;

    private static Table table;

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

        AmazonDynamoDB amazonDynamoDB = AmazonDynamoDBClient.builder().build();

        DynamoDB dynamoDB;
        dynamoDB = new DynamoDB(amazonDynamoDB);

        String awsSamStackName = System.getProperty("AWS_SAM_STACK_NAME");

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

        if (recordTrasnformationTable != null) {
            table = dynamoDB.getTable(recordTrasnformationTable);
        }
    }

    @AfterAll
    public static void runAfterAll() {
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
            DeleteItemOutcome deleteItemOutcome = table.deleteItem("id", key);
            assertNotNull(deleteItemOutcome, "deleteItemOutcome may not be null");
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

            try {
                ResponseBytes<GetObjectResponse> responseBytes = s3Client.getObjectAsBytes(getObjectRequest);

                content = responseBytes.asUtf8String();
            } catch (NoSuchKeyException noSuchKeyException) {
                continue;
            } catch (Exception exception) {
                break;
            }
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

            Item item = table.getItem("id", key, "content", null);
            if (item == null) {
                continue;
            }

            content = (String) item.get("content");
        }

        return content;
    }

}
