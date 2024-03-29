package com.amazon.aws.sample.controller;

import com.amazon.aws.sample.entity.OrderRequest;
import com.amazon.aws.sample.entity.OrderResponse;
import com.amazon.aws.sample.utils.DynamoDBConfig;
import com.amazon.aws.sample.utils.Uuid;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.amazon.aws.sample.exception.OrderException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.sqs.SqsClient;
import software.amazon.awssdk.services.sqs.model.SendMessageRequest;

import javax.validation.Valid;

@RestController
@RequestMapping("/orders")
public class OrderController {
    private static final SqsClient SQS_CLIENT = SqsClient.builder().region(Region.US_EAST_1).build();
    private static final Logger logger = Logger.getLogger(OrderController.class);
    private static final ObjectMapper jsonMapper = new ObjectMapper();
    @Value("${cloud.aws.region.end-point.uri}")
    private String endpoint;
    @Autowired
    private DynamoDBConfig dynamoDBConfig;

    /**
     * This method is used to place order
     * @param request
     * @return
     */
    @PostMapping("/place")
    public ResponseEntity<?> placeOrder(@RequestBody @Valid OrderRequest request) {
        logger.info("Entered api: orders/place");
        try {
            request.setOrderId(Uuid.generateUuid());
            String plainJson = null;
            plainJson = jsonMapper.writeValueAsString(request);
            SendMessageRequest messageRequest = SendMessageRequest.builder()
                    .queueUrl(endpoint)
                    .messageBody(plainJson)
                    .build();
            SQS_CLIENT.sendMessage(messageRequest);
        } catch (Exception e) {
            logger.error("Error while placing order");
        }
        OrderResponse orderResponse = new OrderResponse();
        orderResponse.setMessage("Order Request Sent Successfully");
        orderResponse.setUuid(request.getOrderId());
        return ResponseEntity.ok(orderResponse);
    }

    /**
     * This method is used to getStatusByUuid
     * @param uuid
     * @return
     * @throws Exception
     */
    @GetMapping("/getStatus/{uuid}")
    public ResponseEntity<?> getStatusByUuid(@PathVariable("uuid") String uuid) throws Exception {

        try {
            return ResponseEntity.ok(dynamoDBConfig.getOrderStatus(uuid));
        } catch (RuntimeException e) {
            // Handle any exceptions that occur during the process
            throw new OrderException("OrderId not found");
        }
    }
}
