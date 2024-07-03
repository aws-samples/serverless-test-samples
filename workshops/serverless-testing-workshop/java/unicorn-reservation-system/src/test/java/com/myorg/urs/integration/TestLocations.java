package com.myorg.urs.integration;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import software.amazon.awssdk.services.cloudformation.CloudFormationClient;
import software.amazon.awssdk.services.cloudformation.model.DescribeStacksRequest;
import software.amazon.awssdk.services.cloudformation.model.DescribeStacksResponse;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.AttributeValue;
import software.amazon.awssdk.services.dynamodb.model.GetItemRequest;
import software.amazon.awssdk.services.dynamodb.model.GetItemResponse;
import software.amazon.awssdk.services.dynamodb.model.PutItemRequest;
import software.amazon.awssdk.services.dynamodb.model.PutItemResponse;

public class TestLocations {

    private static String apiEndpoint;

    private static String dynamoDbTableName;

    private static String idPostfix;

    private static String testLocation;

    @BeforeAll
    public static void runBeforeAll() {
        String awsSamStackName = System.getenv("AWS_SAM_STACK_NAME");

        Assertions.assertNotNull(awsSamStackName);

        DescribeStacksRequest describeStacksRequest = DescribeStacksRequest.builder().stackName(awsSamStackName)
                .build();

        CloudFormationClient cloudFormationClient = CloudFormationClient.builder().build();

        DescribeStacksResponse describeStacksResponse = cloudFormationClient.describeStacks(describeStacksRequest);

        Assertions.assertNotNull(describeStacksResponse);

        describeStacksResponse.stacks().forEach(stack -> stack.outputs().forEach(output -> {
            if (output.outputKey().equals("ApiEndpoint")) {
                apiEndpoint = output.outputValue();
            } else if (output.outputKey().equals("DynamoDBTableName")) {
                dynamoDbTableName = output.outputValue();
            }
        }));

        Assertions.assertNotNull(dynamoDbTableName);

        idPostfix = "_%s".formatted(UUID.randomUUID().toString());
        testLocation = "TEST_LOC%s".formatted(idPostfix);

        Map<String, AttributeValue> key = Map.of("PK", AttributeValue.builder().s("LOCATION#LIST").build());

        GetItemRequest getItemRequest = GetItemRequest.builder().tableName(dynamoDbTableName).key(key).build();

        DynamoDbClient dynamoDbClient = DynamoDbClient.builder().build();

        GetItemResponse getItemResponse = dynamoDbClient.getItem(getItemRequest);

        Assertions.assertNotNull(getItemResponse);

        List<AttributeValue> locations = new ArrayList<>();

        if (getItemResponse.hasItem()) {
            List<AttributeValue> existingLocations = getItemResponse.item().get("LOCATIONS").l();

            for (AttributeValue existingLocation : existingLocations) {
                locations.add(existingLocation);
            }
        }

        locations.add(AttributeValue.builder().s(testLocation).build());

        Map<String, AttributeValue> item = Map.of("PK", AttributeValue.builder().s("LOCATION#LIST").build(),
                "LOCATIONS", AttributeValue.builder().l(locations).build());

        PutItemRequest putItemRequest = PutItemRequest.builder().tableName(dynamoDbTableName).item(item).build();

        PutItemResponse putItemResponse = dynamoDbClient.putItem(putItemRequest);

        Assertions.assertNotNull(putItemResponse);
    }

    @Test
    public void testApiGateway200() {
        Assertions.assertNotNull(apiEndpoint);

        CloseableHttpClient closeableHttpClient = HttpClients.createDefault();

        HttpGet httpGet = new HttpGet("%s/locations".formatted(apiEndpoint));

        try (CloseableHttpResponse closeableHttpResponse = closeableHttpClient.execute(httpGet)) {
            Assertions.assertEquals(closeableHttpResponse.getStatusLine().getStatusCode(), 200);

            closeableHttpResponse.close();
        } catch (IOException exception) {
            Assertions.fail(exception);
        }

        try {
            closeableHttpClient.close();
        } catch (IOException exception) {
            Assertions.fail(exception);
        }
    }

    @Test
    public void testLocationsResponse() {
        Assertions.assertNotNull(apiEndpoint);

        CloseableHttpClient closeableHttpClient = HttpClients.createDefault();

        HttpGet httpGet = new HttpGet("%s/locations".formatted(apiEndpoint));

        try (CloseableHttpResponse closeableHttpResponse = closeableHttpClient.execute(httpGet)) {
            String content = EntityUtils.toString(closeableHttpResponse.getEntity());
            Assertions.assertTrue(content.contains(testLocation));

            closeableHttpResponse.close();
        } catch (IOException exception) {
            Assertions.fail(exception);
        }

        try {
            closeableHttpClient.close();
        } catch (IOException exception) {
            Assertions.fail(exception);
        }
    }

    @Test
    public void testApiGateway404() {
        Assertions.assertNotNull(apiEndpoint);

        CloseableHttpClient closeableHttpClient = HttpClients.createDefault();

        HttpGet httpGet = new HttpGet("%s/incorrectxxlocationsxxincorrect".formatted(apiEndpoint));

        try (CloseableHttpResponse closeableHttpResponse = closeableHttpClient.execute(httpGet)) {
            String content = EntityUtils.toString(closeableHttpResponse.getEntity());
            Assertions.assertTrue(content.contains("Missing Authentication Token"));

            closeableHttpResponse.close();
        } catch (IOException exception) {
            Assertions.fail(exception);
        }

        try {
            closeableHttpClient.close();
        } catch (IOException exception) {
            Assertions.fail(exception);
        }
    }

}
