/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: MIT-0
 */

package com.example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import com.example.model.Ticket;
import com.example.utils.DDBUtils;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbEnhancedClient;
import software.amazon.awssdk.http.HttpStatusCode;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;

public class TicketFunction implements RequestHandler<APIGatewayProxyRequestEvent, APIGatewayProxyResponseEvent> {

  private static final Logger logger = LoggerFactory.getLogger(TicketFunction.class);
  private static final ObjectMapper mapper = new ObjectMapper();
  private DDBUtils ddbUtils;

  public TicketFunction(DDBUtils ddbUtils) {
    if (ddbUtils == null) {
      DynamoDbClient ddb = DDBUtils.getDynamoDbClient();
      DynamoDbEnhancedClient enhancedClient = DynamoDbEnhancedClient.builder()
        .dynamoDbClient(ddb)
        .build();
      this.ddbUtils = new DDBUtils(enhancedClient);
    } else {
      this.ddbUtils = ddbUtils;
    }
  }

  public TicketFunction() {
    this(null);
  }

  @Override
  public APIGatewayProxyResponseEvent handleRequest(APIGatewayProxyRequestEvent event, Context context) {

    APIGatewayProxyResponseEvent response = new APIGatewayProxyResponseEvent();

    String ticketId = "";
    try {
      Ticket ticket = mapper.readValue(event.getBody(), Ticket.class);

      logger.info("[ticket userId] " + ticket.getUserId());
      logger.info("[ticket description] " + ticket.getDescription());

      ticketId = ddbUtils.persistTicket(ticket);
      response.setBody(mapper.writeValueAsString(ticketId));

    } catch (JsonProcessingException e) {
      logger.error("Error creating new ticket ", e);
      response.setStatusCode(HttpStatusCode.BAD_REQUEST);
    } catch (Exception e) {
      logger.error("Error creating new ticket ", e);
      response.setStatusCode(HttpStatusCode.INTERNAL_SERVER_ERROR);
    }
    return response;
  }
}
