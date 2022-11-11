/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: MIT-0
 */

package com.example;

import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import com.amazonaws.services.lambda.runtime.tests.annotations.Event;
import com.example.model.Ticket;
import com.example.utils.DDBUtils;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.params.ParameterizedTest;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.MockitoAnnotations;
import software.amazon.awssdk.http.HttpStatusCode;
import software.amazon.awssdk.services.dynamodb.model.DynamoDbException;

import java.util.UUID;

//This is a Unit test that uses Mockito to mock calls to AWS services
public class TicketFunctionMockTest {

  @Mock
  private transient DDBUtils testUtils;
  private transient String uuid = null;
  private TicketFunction function;

  @BeforeEach
  public void beforeEach() {
    MockitoAnnotations.openMocks(this);
    function = new TicketFunction(testUtils);
  }

  @ParameterizedTest
  @Event(value = "events/apigw_request_1.json", type = APIGatewayProxyRequestEvent.class)
  public void testEventDeserialization(APIGatewayProxyRequestEvent event) {
    uuid = UUID.randomUUID().toString();
    Mockito.when(testUtils.persistTicket(Mockito.any(Ticket.class))).thenReturn(uuid);
    APIGatewayProxyResponseEvent response = function.handleRequest(event, null);
    ArgumentCaptor<Ticket> ticketArgumentCaptor = ArgumentCaptor.forClass(Ticket.class);
    Mockito.verify(testUtils).persistTicket(ticketArgumentCaptor.capture());
    Assertions.assertEquals("Lambda rocks", ticketArgumentCaptor.getValue().getDescription());
    Assertions.assertEquals("testuser", ticketArgumentCaptor.getValue().getUserId());
  }

  @ParameterizedTest
  @Event(value = "events/apigw_request_1.json", type = APIGatewayProxyRequestEvent.class)
  public void testPutTicketWithEvent(APIGatewayProxyRequestEvent event) {

    uuid = UUID.randomUUID().toString();
    Mockito.when(testUtils.persistTicket(Mockito.any(Ticket.class))).thenReturn(uuid);

    APIGatewayProxyResponseEvent response = function.handleRequest(event, null);
    Assertions.assertNotNull(response);
    Assertions.assertNotNull(response.getBody());
    Assertions.assertEquals(response.getBody(), "\"" + uuid + "\"");
  }

  @ParameterizedTest
  @Event(value = "events/apigw_request_nobody.json", type = APIGatewayProxyRequestEvent.class)
  public void testPutTicketWithBadEvent(APIGatewayProxyRequestEvent event) {
    APIGatewayProxyResponseEvent response = function.handleRequest(event, null);
    Assertions.assertNotNull(response);
    Assertions.assertEquals(HttpStatusCode.BAD_REQUEST, response.getStatusCode());
  }

  @ParameterizedTest
  @Event(value = "events/apigw_request_1.json", type = APIGatewayProxyRequestEvent.class)
  public void testDynamoDBError(APIGatewayProxyRequestEvent event) {
    Mockito.when(testUtils.persistTicket(Mockito.any(Ticket.class))).thenThrow(DynamoDbException.class);
    APIGatewayProxyResponseEvent response = function.handleRequest(event, null);
    Assertions.assertNotNull(response);
    Assertions.assertEquals(HttpStatusCode.INTERNAL_SERVER_ERROR, response.getStatusCode());
  }
}
