/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: MIT-0
 */

package com.example;

import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import com.amazonaws.services.lambda.runtime.tests.annotations.Event;
import com.example.utils.DDBUtils;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.params.ParameterizedTest;
import org.testcontainers.containers.localstack.LocalStackContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.utility.DockerImageName;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbEnhancedClient;
import software.amazon.awssdk.http.HttpStatusCode;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;

import java.util.ArrayList;
import java.util.List;

import static org.testcontainers.containers.localstack.LocalStackContainer.Service.DYNAMODB;

@Testcontainers
public class TicketFunctionContainerTest {
  private static final DockerImageName localStackImage = DockerImageName.parse("localstack/localstack:1.2.0");
  @Container
  public static final LocalStackContainer localstack = new LocalStackContainer(localStackImage).withServices(DYNAMODB);
  private static DDBUtils ddbUtils;
  private static DynamoDbClient ddbClient;
  private List<String> ticketList = new ArrayList<>();

  @BeforeAll
  static void setup() {
    localstack.start();

    ddbClient = DynamoDbClient.builder()
      .endpointOverride(localstack.getEndpointOverride(DYNAMODB))
      .credentialsProvider(
        StaticCredentialsProvider.create(
          AwsBasicCredentials.create(localstack.getAccessKey(), localstack.getSecretKey())
        )
      )
      .region(Region.of(localstack.getRegion()))
      .build();

    DynamoTestUtil.setupTable(ddbClient);

    DynamoDbEnhancedClient enhancedClient = DynamoDbEnhancedClient.builder()
      .dynamoDbClient(ddbClient)
      .build();

    ddbUtils = new DDBUtils(enhancedClient);
  }

  @AfterAll
  static void cleanup() {
    localstack.stop();
  }


  @ParameterizedTest
  @Event(value = "events/apigw_request_1.json", type = APIGatewayProxyRequestEvent.class)
  public void testPutTicket(APIGatewayProxyRequestEvent event) {
    TicketFunction function = new TicketFunction(ddbUtils);
    APIGatewayProxyResponseEvent response = function.handleRequest(event, null);
    Assertions.assertNotNull(response);
    Assertions.assertNotNull(response.getBody());
    String uuidStr = response.getBody();
    Assertions.assertNotNull(uuidStr);
    ticketList.add(uuidStr.substring(1, uuidStr.length() - 1));
    DynamoTestUtil.validateItems(ticketList, ddbClient);
  }

  @ParameterizedTest
  @Event(value = "events/apigw_request_nobody.json", type = APIGatewayProxyRequestEvent.class)
  public void testPutTicketBadRequest(APIGatewayProxyRequestEvent event) {
    TicketFunction function = new TicketFunction(ddbUtils);
    APIGatewayProxyResponseEvent response = function.handleRequest(event, null);
    Assertions.assertNotNull(response);
    Assertions.assertEquals(HttpStatusCode.BAD_REQUEST, response.getStatusCode());
  }

}
