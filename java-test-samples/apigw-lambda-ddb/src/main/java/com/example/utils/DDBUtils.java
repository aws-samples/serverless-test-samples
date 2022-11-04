/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: MIT-0
 */

package com.example.utils;

import com.example.model.Ticket;
import software.amazon.awssdk.auth.credentials.EnvironmentVariableCredentialsProvider;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbEnhancedClient;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbTable;
import software.amazon.awssdk.enhanced.dynamodb.TableSchema;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;

import java.util.UUID;

public class DDBUtils {

  private DynamoDbEnhancedClient enhancedClient;

  public DDBUtils() {
    this(null);
  }

  public DDBUtils(DynamoDbEnhancedClient enhancedClient) {
    if (enhancedClient == null) {
      DynamoDbClient ddb = DynamoDbClient.builder()
        .credentialsProvider(EnvironmentVariableCredentialsProvider.create())
        .region(Region.US_EAST_1)
        .build();
      this.enhancedClient = enhancedClient = DynamoDbEnhancedClient.builder()
        .dynamoDbClient(ddb)
        .build();
    } else {
      this.enhancedClient = enhancedClient;
    }

  }


  public String persistTicket(Ticket ticket) {

    DynamoDbTable<Ticket> mappedTable = enhancedClient
      .table("tickets", TableSchema.fromBean(Ticket.class));

    String ticketId = UUID.randomUUID().toString();

    ticket.setTicketId(ticketId);

    mappedTable.putItem(ticket);

    return ticketId;
  }
}
