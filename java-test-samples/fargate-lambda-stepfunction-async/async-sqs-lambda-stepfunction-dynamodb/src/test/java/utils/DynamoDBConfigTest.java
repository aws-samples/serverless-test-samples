package utils;

import com.amazon.aws.sample.utils.AmazonDynamoDBClientBuilderService;
import com.amazon.aws.sample.utils.DynamoDBConfig;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.model.AttributeValue;
import com.amazonaws.services.dynamodbv2.model.GetItemRequest;
import com.amazonaws.services.dynamodbv2.model.GetItemResult;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.MockitoJUnitRunner;
import org.springframework.boot.autoconfigure.context.PropertyPlaceholderAutoConfiguration;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.HashMap;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.when;

@RunWith(MockitoJUnitRunner.class)
@SpringBootTest(classes = {PropertyPlaceholderAutoConfiguration.class, DynamoDBConfig.class})
public class DynamoDBConfigTest {
    @Mock
    private AmazonDynamoDB amazonDynamoDBMock;
    @Mock
    private AmazonDynamoDBClientBuilderService amazonDynamoDBClientBuilderService;
    @InjectMocks
    private DynamoDBConfig dynamoDBConfig;

    private static final String orderId = "abee61d5-e180-4d01-bdb5-f7ce31562a81";

    @Test
    public void testGetOrderStatus() {
        when(amazonDynamoDBClientBuilderService.buildClient()).thenReturn(amazonDynamoDBMock);

        GetItemRequest request = new GetItemRequest();
        request.setTableName("order_details");
        request.setProjectionExpression("orderStatus");
        Map<String, AttributeValue> keysMap = new HashMap<>();
        keysMap.put("orderId", new AttributeValue(orderId));
        request.setKey(keysMap);

        GetItemResult result = new GetItemResult();
        Map<String, AttributeValue> item = new HashMap<>();
        item.put("orderStatus", new AttributeValue().withS("Order Placed"));
        result.setItem(item);

        when(amazonDynamoDBMock.getItem(request)).thenReturn(result);
        dynamoDBConfig.getOrderStatus(orderId);
        assertThat(result.getItem().get("orderStatus").getS()).isEqualTo("Order Placed");
    }
}
