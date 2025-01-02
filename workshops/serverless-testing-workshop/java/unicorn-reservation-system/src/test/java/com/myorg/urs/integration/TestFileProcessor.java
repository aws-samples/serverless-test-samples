package com.myorg.urs.integration;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.cloudformation.CloudFormationClient;
import software.amazon.awssdk.services.cloudformation.model.DescribeStacksRequest;
import software.amazon.awssdk.services.cloudformation.model.DescribeStacksResponse;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.AttributeValue;
import software.amazon.awssdk.services.dynamodb.model.DeleteItemRequest;
import software.amazon.awssdk.services.dynamodb.model.DeleteItemResponse;
import software.amazon.awssdk.services.dynamodb.model.GetItemRequest;
import software.amazon.awssdk.services.dynamodb.model.GetItemResponse;
import software.amazon.awssdk.services.dynamodb.model.PutItemRequest;
import software.amazon.awssdk.services.dynamodb.model.PutItemResponse;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;
import software.amazon.awssdk.services.s3.model.PutObjectResponse;

public class TestFileProcessor {

    private static S3Client s3Client;

    private static String dynamoDbTableName;

    private static String unicornInventoryBucket;

    private static String idPostfix;

    private static String testUnicorn;

    private static String testLocation;

    @BeforeAll
    public static void runBeforeAll() {
        s3Client = S3Client.builder()
                .httpClient(ApacheHttpClient.create())
                .build();

        String awsSamStackName = System.getenv("AWS_SAM_STACK_NAME");

        Assertions.assertNotNull(awsSamStackName);

        DescribeStacksRequest describeStacksRequest = DescribeStacksRequest.builder().stackName(awsSamStackName)
                .build();

        CloudFormationClient cloudFormationClient = CloudFormationClient.builder().build();

        DescribeStacksResponse describeStacksResponse = cloudFormationClient.describeStacks(describeStacksRequest);

        Assertions.assertNotNull(describeStacksResponse);

        describeStacksResponse.stacks().forEach(stack -> stack.outputs().forEach(output -> {
            if (output.outputKey().equals("DynamoDBTableName")) {
                dynamoDbTableName = output.outputValue();
            } else if (output.outputKey().equals("UnicornInventoryBucket")) {
                unicornInventoryBucket = output.outputValue();
            }
        }));

        Assertions.assertNotNull(dynamoDbTableName);
        Assertions.assertNotNull(unicornInventoryBucket);

        idPostfix = "_%s".formatted(UUID.randomUUID().toString());
        testUnicorn = "TEST_UNI%s".formatted(idPostfix);
        testLocation = "TEST_LOC%s".formatted(idPostfix);
    }

    @AfterAll
    public static void runAfterAll() {
        // Delete testUnicorn
        Map<String, AttributeValue> key = Map.of("PK", AttributeValue.builder().s(testUnicorn).build());

        GetItemRequest getItemRequest = GetItemRequest.builder().tableName(dynamoDbTableName).key(key).build();

        DynamoDbClient dynamoDbClient = DynamoDbClient.builder().build();

        GetItemResponse getItemResponse = dynamoDbClient.getItem(getItemRequest);

        if (getItemResponse.hasItem()) {
            DeleteItemRequest deleteItemRequest = DeleteItemRequest.builder().tableName(dynamoDbTableName).key(key)
                    .build();

            DeleteItemResponse deleteItemResponse = dynamoDbClient.deleteItem(deleteItemRequest);

            Assertions.assertNotNull(deleteItemResponse);
        }

        // Update LOCATION#LIST without testLocation
        key = Map.of("PK", AttributeValue.builder().s("LOCATION#LIST").build());

        getItemRequest = GetItemRequest.builder().tableName(dynamoDbTableName).key(key).build();

        dynamoDbClient = DynamoDbClient.builder().build();

        getItemResponse = dynamoDbClient.getItem(getItemRequest);

        Assertions.assertNotNull(getItemResponse);

        List<AttributeValue> locations = getItemResponse.item().get("LOCATIONS").l();

        List<AttributeValue> updatedLocations = new ArrayList<>();

        for (AttributeValue location : locations) {
            if (!location.s().equals(testLocation)) {
                updatedLocations.add(location);
            }
        }

        Map<String, AttributeValue> item = Map.of("PK", AttributeValue.builder().s("LOCATION#LIST").build(),
                "LOCATIONS", AttributeValue.builder().l(updatedLocations).build());

        PutItemRequest putItemRequest = PutItemRequest.builder().tableName(dynamoDbTableName).item(item).build();

        PutItemResponse putItemResponse = dynamoDbClient.putItem(putItemRequest);

        Assertions.assertNotNull(putItemResponse);
    }

    @Test
    public void testFileProcessorHappyPath() {
        Map<String, AttributeValue> key = Map.of("PK", AttributeValue.builder().s(testUnicorn).build());

        GetItemRequest getItemRequest = GetItemRequest.builder().tableName(dynamoDbTableName).key(key).build();

        DynamoDbClient dynamoDbClient = DynamoDbClient.builder().build();

        GetItemResponse getItemResponse = dynamoDbClient.getItem(getItemRequest);

        Assertions.assertFalse(getItemResponse.hasItem());

        String testDataCsv = "\"Unicorn Name\",\"Unicorn Location\"\n";
        testDataCsv += "\"%s\",\"%s\"\n".formatted(testUnicorn, testLocation);

        String testDataKey = "INTEGRATION_TEST/TEST%s.test_file_processor_happy_path.csv".formatted(idPostfix);

        PutObjectRequest putObjectRequest = PutObjectRequest.builder().bucket(unicornInventoryBucket)
                .key(testDataKey).build();

        PutObjectResponse putObjectResponse = s3Client.putObject(putObjectRequest, RequestBody.fromString(testDataCsv));
        Assertions.assertNotNull(putObjectResponse);

        int pollMaxSeconds = 30;
        int pollCompleteSeconds = 0;

        while (pollCompleteSeconds < pollMaxSeconds) {
            getItemResponse = dynamoDbClient.getItem(getItemRequest);

            if (getItemResponse.hasItem()) {
                break;
            }

            try {
                Thread.sleep(1000);
            } catch (InterruptedException exception) {
                Assertions.fail(exception);
            }

            pollCompleteSeconds++;
        }

        Assertions.assertTrue(getItemResponse.hasItem(), "Item not found after time allowed for processing.");
        Assertions.assertTrue((pollCompleteSeconds <= 2),
                "Unicorns should be fast! Took too long: %d sec".formatted(pollCompleteSeconds));
        Assertions.assertEquals(getItemResponse.item().get("PK").s(), testUnicorn,
                "Table PK is not set to the Unicorn Name: %s expected %s"
                        .formatted(getItemResponse.item().get("PK").s(), testUnicorn));
        Assertions.assertEquals(getItemResponse.item().get("LOCATION").s(), testLocation,
                "Table LOCATION is not set to the Unicorn Location: %s expected %s"
                        .formatted(getItemResponse.item().get("LOCATION").s(), testLocation));
    }

}