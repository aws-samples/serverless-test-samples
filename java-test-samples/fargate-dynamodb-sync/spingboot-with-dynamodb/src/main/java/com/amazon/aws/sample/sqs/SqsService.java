package com.amazon.aws.sample.sqs;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import com.amazonaws.regions.Regions;
import com.amazonaws.services.sqs.AmazonSQS;
import com.amazonaws.services.sqs.AmazonSQSClientBuilder;
import com.amazonaws.services.sqs.model.AmazonSQSException;
import com.amazonaws.services.sqs.model.CreateQueueResult;
import com.amazonaws.services.sqs.model.SendMessageRequest;

@Service
public class SqsService {

    @Value("${aws.sqs.queue.name}")
    public String queueName;
    @Value("${aws.sqs.queue.message}")
    public String queueMessage;

    public void sendMessage(){
        final AmazonSQS sqs = AmazonSQSClientBuilder.standard()
                .withRegion(Regions.US_EAST_1).build();

        try {
            CreateQueueResult createResult = sqs.createQueue(queueName);
        } catch (AmazonSQSException e) {
            if (!e.getErrorCode().equals("QueueAlreadyExists")) {
                throw e;
            }
        }

        String queueUrl = sqs.getQueueUrl(queueName).getQueueUrl();

        SendMessageRequest sendMsgRequest = new SendMessageRequest()
                .withQueueUrl(queueUrl)
                .withMessageBody(queueMessage)
                .withDelaySeconds(5);
        sqs.sendMessage(sendMsgRequest);
    }
}
