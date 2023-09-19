package com.example;

import java.io.IOException;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

import com.fasterxml.jackson.databind.JsonNode;

public class ContractTest extends BaseJsonSchemaValidatorTest {

    @Test
    public void testAddressHasFourFields() throws IOException{
        JsonNode jsonNode = getJsonNodeFromClasspath("events/customerCreated-event-1.1.0.json");
        CustomerValidator validator = new CustomerValidator();
        // Check for business logic in address validation
        Assertions.assertTrue(validator.isValidAddress(jsonNode));    
    }

    @Test
    public void testAddressHasThreeFieldsOrLess() throws IOException{
        JsonNode jsonNode = getJsonNodeFromClasspath("events/customerCreated-event-1.4.0.json");
        CustomerValidator validator = new CustomerValidator();
        // Check for business logic in address validation
        Assertions.assertFalse(validator.isValidAddress(jsonNode));    
    }
    
}
