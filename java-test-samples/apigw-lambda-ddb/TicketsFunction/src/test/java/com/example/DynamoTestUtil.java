/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: MIT-0
 */

package com.example;

import org.junit.jupiter.api.Assertions;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class DynamoTestUtil {

  private static final String DB_TABLE = "tickets";
  private static final String key = "ticketId";

  static void setupTable(DynamoDbClient ddbClient) {
    ddbClient.createTable(CreateTableRequest.builder()
      .tableName(DB_TABLE)
      .attributeDefinitions(AttributeDefinition.builder()
        .attributeName(key)
        .attributeType(ScalarAttributeType.S)
        .build())
      .keySchema(KeySchemaElement.builder()
        .attributeName(key)
        .keyType(KeyType.HASH)
        .build())
      .provisionedThroughput(ProvisionedThroughput.builder()
        .readCapacityUnits(10L)
        .writeCapacityUnits(10L)
        .build())
      .build());
  }

  static void validateItems(List<String> ticketList, DynamoDbClient ddbClient) {
    ticketList.forEach(ticketId -> {
      Map<String, AttributeValue> keyMap = new HashMap<>();
      keyMap.put(key, AttributeValue.builder().s(ticketId).build());
      GetItemResponse response = ddbClient.getItem(GetItemRequest.builder()
        .tableName(DB_TABLE)
        .key(keyMap)
        .build());
      Assertions.assertTrue(response.hasItem());
    });
  }

  static void deleteFromDDBTable(DynamoDbClient ddbClient, List<String> ticketList) {
    ticketList.forEach(ticketId -> {
      HashMap<String, AttributeValue> keyToGet = new HashMap<>();
      keyToGet.put("ticketId", AttributeValue.builder()
        .s(ticketId)
        .build());

      DeleteItemRequest deleteReq = DeleteItemRequest.builder()
        .tableName(DB_TABLE)
        .key(keyToGet)
        .build();

      try {
        ddbClient.deleteItem(deleteReq);
      } catch (DynamoDbException e) {
        System.err.println(e.getMessage());
      }
    });
  }
}
