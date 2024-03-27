package com.amazon.aws.sample.utils;

import com.amazonaws.regions.Regions;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClientBuilder;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class AmazonDynamoDBClientServiceImpl implements AmazonDynamoDBClientBuilderService {

    @Value("${cloud.aws.region.static}")
    private String region;
    @Override
    public AmazonDynamoDB buildClient() {
        return AmazonDynamoDBClientBuilder.standard()
                .withRegion(region).build();
    }
}
