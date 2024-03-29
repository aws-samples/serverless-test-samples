package com.amazon.aws.sample.utils;

import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.model.AttributeValue;
import com.amazonaws.services.dynamodbv2.model.GetItemRequest;
import com.amazonaws.services.dynamodbv2.model.GetItemResult;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;

import java.util.HashMap;
import java.util.Map;

@Configuration
public class DynamoDBConfig {

    @Autowired
    AmazonDynamoDBClientBuilderService amazonDynamoDBClientBuilderService;

    /**
     * This method is used to getOrderStatus from dynamoDb
     * @param orderId
     * @return
     */
    public String getOrderStatus(String orderId) {
        AmazonDynamoDB client = amazonDynamoDBClientBuilderService.buildClient();
        GetItemRequest request = new GetItemRequest();

        /* Setting Table Name */
        request.setTableName("order_details");
        /* Setting Name of attributes to Get */
        request.setProjectionExpression("orderStatus");
        /* Create a Map of Primary Key attributes */
        Map<String, AttributeValue> keysMap = new HashMap<>();
        keysMap.put("orderId", new AttributeValue(orderId));
        request.setKey(keysMap);
        /* Send Get Item Request */
        GetItemResult result = client.getItem(request);
        return String.valueOf(result.getItem().get("orderStatus").getS());
    }

}
