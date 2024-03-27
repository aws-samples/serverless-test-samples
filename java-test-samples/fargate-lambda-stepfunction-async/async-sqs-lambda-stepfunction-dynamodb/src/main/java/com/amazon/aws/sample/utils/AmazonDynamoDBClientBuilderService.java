package com.amazon.aws.sample.utils;

import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import org.springframework.stereotype.Service;

@Service
public interface AmazonDynamoDBClientBuilderService {
    AmazonDynamoDB buildClient();
}
