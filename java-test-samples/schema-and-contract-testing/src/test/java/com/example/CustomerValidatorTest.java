package com.example;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;

import org.junit.jupiter.api.Test;

import com.fasterxml.jackson.databind.JsonNode;

public class CustomerValidatorTest extends BaseJsonSchemaValidatorTest {

    @Test
    public void validateAddressFieldRuleWithCorrectPayload() throws IOException{
        JsonNode payload = getJsonNodeFromClasspath("events/customerCreated-event-1.1.0.json");
        CustomerValidator customerValidator = new CustomerValidator();
        assertTrue(customerValidator.isValidAddress(payload));
    }

    @Test
    public void validateAddressFieldRuleWithIncorrectPayload() throws IOException{
        JsonNode payload = getJsonNodeFromClasspath("events/customerCreated-event-1.4.0.json");
        CustomerValidator customerValidator = new CustomerValidator();
        assertFalse(customerValidator.isValidAddress(payload));
    
    }
    
}
