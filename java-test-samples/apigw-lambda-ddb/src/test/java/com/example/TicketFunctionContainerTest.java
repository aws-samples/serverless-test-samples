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
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;

import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.List;

import static org.testcontainers.containers.localstack.LocalStackContainer.Service.DYNAMODB;

@Testcontainers
public class TicketFunctionContainerTest {
  private static DDBUtils ddbUtils;
  private static DynamoDbClient ddbClient;
  private static final DockerImageName localStackImage = DockerImageName.parse("localstack/localstack:0.14.3");
  @Container
  public static final LocalStackContainer localstack = new LocalStackContainer(localStackImage).withServices(DYNAMODB);
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

    ddbUtils = new DDBUtils();
    //Use Reflection to inject private field
    try {
      Field field = DDBUtils.class.getDeclaredField("enhancedClient");
      field.setAccessible(true);
      field.set(ddbUtils, enhancedClient);
    } catch (Exception e) {
      e.printStackTrace();
      Assertions.fail();
    }
  }

  @AfterAll
  static void cleanup() {
    localstack.stop();
  }


  @ParameterizedTest
  @Event(value = "events/apigw_request_1.json", type = APIGatewayProxyRequestEvent.class)
  public void testPutTicket(APIGatewayProxyRequestEvent event) {
    try {
      TicketFunction function = new TicketFunction();
      //Use Reflection to inject private field
      Field field = TicketFunction.class.getDeclaredField("ddbUtils");
      field.setAccessible(true);
      field.set(function, ddbUtils);

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

}