/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: MIT-0
 */

package com.example;

import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import com.amazonaws.services.lambda.runtime.tests.annotations.Event;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.extension.ExtendWith;
import org.junit.jupiter.params.ParameterizedTest;
import software.amazon.awssdk.auth.credentials.AwsCredentials;
import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import uk.org.webcompere.systemstubs.environment.EnvironmentVariables;
import uk.org.webcompere.systemstubs.jupiter.SystemStub;
import uk.org.webcompere.systemstubs.jupiter.SystemStubsExtension;

import java.util.ArrayList;
import java.util.List;

// This is an integration test as it requires an actual AWS account.
// It assumes that a DynamoDB table with name "tickets" exists on AWS in US-EAST-1
// and reads AWS Credentials from ~/.aws/credentials with default profile
@ExtendWith(SystemStubsExtension.class)
public class TicketFunctionIntegrationTest {

  @SystemStub
  private EnvironmentVariables environmentVariables;

  private final DynamoDbClient ddbClient = DynamoDbClient.builder()
    .region(Region.US_EAST_1)
    .build();

  private List<String> ticketList = new ArrayList<>();

  @BeforeEach
  public void setup() {
    ProfileCredentialsProvider credentialsProvider = ProfileCredentialsProvider.create("default");
    AwsCredentials awsCredentials = credentialsProvider.resolveCredentials();
    environmentVariables.set("AWS_ACCESS_KEY_ID", awsCredentials.accessKeyId());
    environmentVariables.set("AWS_SECRET_ACCESS_KEY", awsCredentials.secretAccessKey());
  }

  @AfterEach
  public void cleanup() {
    DynamoTestUtil.deleteFromDDBTable(ddbClient, ticketList);
    ticketList.clear();
  }

  @ParameterizedTest
  @Event(value = "events/apigw_request_1.json", type = APIGatewayProxyRequestEvent.class)
  public void testPutTicket(APIGatewayProxyRequestEvent event, EnvironmentVariables environmentVariables) {
    try {
      TicketFunction function = new TicketFunction();
      APIGatewayProxyResponseEvent response = function.handleRequest(event, null);
      Assertions.assertNotNull(response);
      Assertions.assertNotNull(response.getBody());
      String uuidStr = response.getBody();
      Assertions.assertNotNull(uuidStr);
      ticketList.add(uuidStr.substring(1, uuidStr.length() - 1));
      DynamoTestUtil.validateItems(ticketList, ddbClient);
    } catch (Exception e) {
      e.printStackTrace();
      Assertions.fail();
    }
  }

  @ParameterizedTest
  @Event(value = "events/apigw_request_nobody.json", type = APIGatewayProxyRequestEvent.class)
  public void testPutTicketBadRequest(APIGatewayProxyRequestEvent event, EnvironmentVariables environmentVariables) {
    try {
      TicketFunction function = new TicketFunction();
      APIGatewayProxyResponseEvent response = function.handleRequest(event, null);
      Assertions.assertNotNull(response);
      Assertions.assertNull(response.getBody());
    } catch (Exception e) {
      e.printStackTrace();
      Assertions.fail();
    }
  }

}
