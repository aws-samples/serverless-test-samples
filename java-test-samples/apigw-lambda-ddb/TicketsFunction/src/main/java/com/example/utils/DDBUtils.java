/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: MIT-0
 */

package com.example.utils;

import com.amazonaws.xray.interceptors.TracingInterceptor;
import com.example.model.Ticket;
import software.amazon.awssdk.auth.credentials.EnvironmentVariableCredentialsProvider;
import software.amazon.awssdk.core.SdkSystemSetting;
import software.amazon.awssdk.core.client.config.ClientOverrideConfiguration;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbEnhancedClient;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbTable;
import software.amazon.awssdk.enhanced.dynamodb.TableSchema;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;

import java.util.UUID;

public class DDBUtils {

  private DynamoDbEnhancedClient enhancedClient;

  public DDBUtils(DynamoDbEnhancedClient enhancedClient) {
    if (enhancedClient == null) {
      DynamoDbClient ddb = getDynamoDbClient();
      this.enhancedClient = DynamoDbEnhancedClient.builder()
        .dynamoDbClient(ddb)
        .build();
    } else {
      this.enhancedClient = enhancedClient;
    }

  }

  public static DynamoDbClient getDynamoDbClient() {
    DynamoDbClient ddb = DynamoDbClient.builder()
      .credentialsProvider(EnvironmentVariableCredentialsProvider.create())
      .region(Region.of(System.getenv(SdkSystemSetting.AWS_REGION.environmentVariable())))
      .overrideConfiguration(ClientOverrideConfiguration.builder()
        .addExecutionInterceptor(new TracingInterceptor())
        .build())
      .build();
    return ddb;
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
