/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: MIT-0
 */

package com.example;

import io.restassured.RestAssured;
import io.restassured.response.Response;
import org.junit.Assert;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.cloudformation.CloudFormationClient;
import software.amazon.awssdk.services.cloudformation.model.DescribeStacksRequest;
import software.amazon.awssdk.services.cloudformation.model.DescribeStacksResponse;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;

import java.util.ArrayList;
import java.util.List;

// This test requires an AWS account and assumes the SAM template part of this repo is deployed to AWS
// This test runs END 2 END by sending an HTTP request to API Gateway URL and
// verifies if entries are persisted in DDB
public class TicketEnd2EndTest {
  //Name of the stack you used when deploying SAM template
  private static final String STACK_NAME = "APIGW-Lambda-DDB-Sample";
  private static DynamoDbClient ddbClient;
  private static CloudFormationClient cloudFormationClient;
  private static String apiEndPoint = "";
  private List<String> ticketList = new ArrayList<>();

  @BeforeAll
  static void setUp() {
    ddbClient = DynamoDbClient.builder()
      .region(Region.US_EAST_1)
      .build();

    cloudFormationClient = CloudFormationClient
      .builder().region(Region.US_EAST_1).build();

    DescribeStacksResponse response = cloudFormationClient.describeStacks(DescribeStacksRequest.builder()
      .stackName(STACK_NAME)
      .build());
    apiEndPoint = response.stacks().get(0).outputs().get(0).outputValue();
  }

  @AfterEach
  public void cleanup() {
    DynamoTestUtil.deleteFromDDBTable(ddbClient, ticketList);
    ticketList.clear();
  }

  @Test
  public void testPost() {
    Response response = RestAssured.given()
      .header("Content-Type", "application/json")
      .header("Accept", "application/json")
      .body("{\"description\": \"Lambda rocks\", \"userId\": \"testuser\"}")
      .when()
      .post(apiEndPoint);

    Assertions.assertEquals(response.statusCode(), 200);
    String ticketId = response.asString();
    Assert.assertNotNull(ticketId);
    ticketList.add(ticketId.substring(1, ticketId.length() - 1));
    DynamoTestUtil.validateItems(ticketList, ddbClient);
  }

  @Test
  public void testPostWithBadPayload() {
    Response response = RestAssured.given()
      .header("Content-Type", "application/json")
      .header("Accept", "application/json")
      .body("{\"description\":, \"userId\": \"testuser\"}")
      .when()
      .post(apiEndPoint);

    Assertions.assertEquals(response.statusCode(), 400);
  }
}