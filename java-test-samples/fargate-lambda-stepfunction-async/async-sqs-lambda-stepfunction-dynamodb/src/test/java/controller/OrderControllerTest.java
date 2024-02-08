package controller;

import com.amazon.aws.sample.controller.OrderController;
import com.amazon.aws.sample.entity.OrderRequest;
import com.amazon.aws.sample.entity.OrderResponse;
import com.amazon.aws.sample.utils.DynamoDBConfig;
import com.amazon.aws.sample.utils.Uuid;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.model.AttributeValue;
import com.amazonaws.services.dynamodbv2.model.GetItemRequest;
import com.amazonaws.services.dynamodbv2.model.GetItemResult;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.amazon.aws.sample.exception.OrderException;
import org.junit.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.junit.runner.RunWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.MockitoAnnotations;
import org.mockito.junit.MockitoJUnitRunner;
import org.springframework.boot.autoconfigure.context.PropertyPlaceholderAutoConfiguration;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.ResponseEntity;
import software.amazon.awssdk.services.sqs.SqsClient;
import software.amazon.awssdk.services.sqs.model.SendMessageRequest;

import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.Assert.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;

@RunWith(MockitoJUnitRunner.class)
@SpringBootTest(classes = {PropertyPlaceholderAutoConfiguration.class, DynamoDBConfig.class})
public class OrderControllerTest {
    @Mock
    private AmazonDynamoDB amazonDynamoDBMock;
    @Mock
    private DynamoDBConfig dynamoDBConfig;
    @InjectMocks
    private OrderController orderController;

    private static final String orderId = "abee61d5-e180-4d01-bdb5-f7ce31562a81";

    @Test
    public void testPlaceOrder() throws JsonProcessingException {
        OrderRequest request = new OrderRequest();
        request.setOrderId(Uuid.generateUuid());
        ObjectMapper objectMapper = new ObjectMapper();
        String plainJson = objectMapper.writeValueAsString(request);
        SqsClient sqsClientMock = mock(SqsClient.class);

        SendMessageRequest mockMessageRequest = SendMessageRequest.builder()
                .queueUrl("endpoint")
                .messageBody(plainJson)
                .build();
        sqsClientMock.sendMessage(mockMessageRequest);
        verify(sqsClientMock).sendMessage(mockMessageRequest);
        OrderRequest orderRequest = new OrderRequest();
        ResponseEntity<?> response = orderController.placeOrder(orderRequest);
        verify(sqsClientMock).sendMessage(any(SendMessageRequest.class));
        assertThat(response.getStatusCode().value()).isEqualTo(200);
        OrderResponse orderResponse = (OrderResponse) response.getBody();
        assertThat(orderResponse.getMessage()).isEqualTo("Order Request Sent Successfully");
        assertThat(orderResponse.getUuid()).isNotNull();
    }

    @Test
    public void testGetStatusByUuid() throws Exception {
        GetItemResult result = new GetItemResult().withItem(Map.of("orderStatus", new AttributeValue("Order Request Sent Successfully")));
        Mockito.lenient().when(amazonDynamoDBMock.getItem(any(GetItemRequest.class))).thenReturn(result);
        dynamoDBConfig.getOrderStatus(orderId);
        ResponseEntity<String> res = ResponseEntity.ok("Order Placed");
        orderController.getStatusByUuid(orderId);
        assertThat(result.getItem().get("orderStatus").getS()).isEqualTo("Order Request Sent Successfully");
    }

    @Test
    public void testGetOrderStatusThrowsException() {
        Mockito.when(dynamoDBConfig.getOrderStatus(orderId)).thenThrow(new OrderException("OrderId not found"));
        assertThrows(OrderException.class, () -> orderController.getStatusByUuid(orderId));
    }
}
