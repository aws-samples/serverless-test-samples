package com.amazon.aws.sample;


import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import com.amazon.aws.sample.model.Customer;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClientBuilder;
import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBMapper;
import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBMapperConfig;
import com.amazonaws.services.dynamodbv2.model.CreateTableRequest;
import com.amazonaws.services.dynamodbv2.model.ProvisionedThroughput;
import com.amazonaws.services.dynamodbv2.util.TableUtils;

@Configuration
public class DynamoDBConfig {
    private static final Logger logger = LoggerFactory.getLogger(DynamoDBConfig.class);

    @Value("${cloud.aws.region.static}")
    public String region;

    @Bean
    public DynamoDBMapper dynamoDBMapper() {
        AmazonDynamoDB client = AmazonDynamoDBClientBuilder.standard()
                .withRegion(region).build();
        DynamoDBMapper dynamoDBMapper = new DynamoDBMapper(client, DynamoDBMapperConfig.DEFAULT);
        init(dynamoDBMapper, client);
        return dynamoDBMapper;
    }
    // Initializes the DynamoDB table for the Customer class
    public void init(DynamoDBMapper dynamoDBMapper, AmazonDynamoDB client) {

        // Generates a CreateTableRequest based on the Customer class mapping
        CreateTableRequest tableRequest = dynamoDBMapper.generateCreateTableRequest(Customer.class);
        tableRequest.setProvisionedThroughput(new ProvisionedThroughput(1L, 1L));
        // Sets the provisioned throughput for the table (adjust as needed)
        if (TableUtils.createTableIfNotExists(client, tableRequest)) {
            // Creates the table if it doesn't already exist, logging a message on success
            logger.info("Table created successfully");
        }
    }
}
