/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: MIT-0
 */

package com.example;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.cloudformation.CloudFormationClient;
import software.amazon.awssdk.services.cloudformation.model.DescribeStacksRequest;
import software.amazon.awssdk.services.cloudformation.model.DescribeStacksResponse;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;

// This test requires an AWS account and assumes the SAM template part of this repo is deployed to AWS
// This test runs END 2 END by HTTP request to API Gateway URL and
// verifies if entries are persisted in DDB
public class TicketEnd2EndTest {
  private static DynamoDbClient ddbClient;
  private static CloudFormationClient cloudFormationClient;
  private List<String> ticketList = new ArrayList<>();

  //Name of the stack you used when deploying SAm template
  private static final String STACK_NAME = "APIGW-Lambda-DDB-Sample";
  private static String endPoint = "";

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
    endPoint = response.stacks().get(0).outputs().get(0).outputValue();
  }

  @AfterEach
  public void cleanup() {
    DynamoTestUtil.deleteFromDDBTable(ddbClient, ticketList);
    ticketList.clear();
  }

  @Test
  public void testPost() {
    try {
      URL url = new URL(endPoint);
      HttpURLConnection con = (HttpURLConnection) url.openConnection();
      con.setRequestMethod("POST");
      con.setRequestProperty("Content-Type", "application/json");
      con.setRequestProperty("Accept", "application/json");
      con.setDoOutput(true);
      String jsonInputString = "{\"description\": \"Lambda rocks\", \"userId\": \"testuser\"}";
      try (OutputStream os = con.getOutputStream()) {
        byte[] input = jsonInputString.getBytes("utf-8");
        os.write(input, 0, input.length);
      }
      try (BufferedReader br = new BufferedReader(
        new InputStreamReader(con.getInputStream(), "utf-8"))) {
        StringBuilder httpResponse = new StringBuilder();
        String responseLine = null;
        while ((responseLine = br.readLine()) != null) {
          httpResponse.append(responseLine.trim());
        }
        String ticketId = httpResponse.toString();
        ticketList.add(ticketId.substring(1, ticketId.length() - 1));
        DynamoTestUtil.validateItems(ticketList, ddbClient);
      }
    } catch (Exception e) {
      e.printStackTrace();
      Assertions.fail(e.getMessage());
    }
  }
}