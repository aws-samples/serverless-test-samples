package com.example;

import java.io.IOException;
import java.util.Set;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

import com.fasterxml.jackson.databind.JsonNode;
import com.networknt.schema.JsonSchema;
import com.networknt.schema.ValidationMessage;

/**
 * Unit test for simple App.
 */
public class SchemaTest extends BaseJsonSchemaValidatorTest{
    @Test
    public void addAdditionalOptionalAttribute() throws IOException{
        JsonSchema originSchema = getJsonSchemaFromClasspath("schema/json/customerCreated-v1.0.0.json");
        JsonSchema updatedSchema = getJsonSchemaFromClasspath("schema/json/customerCreated-v1.1.0.json");

        JsonNode jsonNodeNewVersion = getJsonNodeFromClasspath("events/customerCreated-event-1.1.0.json");

        originSchema.initializeValidators();
        updatedSchema.initializeValidators();

        // validate json payload to its own schema
        Set<ValidationMessage> validationMessages = updatedSchema.validate(jsonNodeNewVersion);
        Assertions.assertTrue(validationMessages.isEmpty());

        // check for backward compatibility
        Set<ValidationMessage> validationMessages2 = originSchema.validate(jsonNodeNewVersion);
        Assertions.assertTrue(validationMessages2.isEmpty());
        
    }

    @Test
    public void addAdditionalRequiredAttribute() throws IOException{
        JsonSchema originSchema = getJsonSchemaFromClasspath("schema/json/customerCreated-v1.0.0.json");
        JsonSchema updatedSchema = getJsonSchemaFromClasspath("schema/json/customerCreated-v1.2.0.json");

        JsonNode jsonNodeNewVersion = getJsonNodeFromClasspath("events/customerCreated-event-1.2.0.json");

        originSchema.initializeValidators();
        updatedSchema.initializeValidators();

        // validate new json payload to its own schema
        Set<ValidationMessage> validationMessages = updatedSchema.validate(jsonNodeNewVersion);
        Assertions.assertTrue(validationMessages.isEmpty());

        // check for backward compatibility to its original/old schema
        Set<ValidationMessage> validationMessages2 = originSchema.validate(jsonNodeNewVersion);
        Assertions.assertTrue(validationMessages2.isEmpty());
            
    }

    @Test
    public void removingRequiredAttribute() throws IOException{
        JsonSchema originSchema = getJsonSchemaFromClasspath("schema/json/customerCreated-v1.0.0.json");
        JsonSchema updatedSchema = getJsonSchemaFromClasspath("schema/json/customerCreated-v1.3.0.json");

        JsonNode jsonNodeNewVersion = getJsonNodeFromClasspath("events/customerCreated-event-1.3.0.json");

        originSchema.initializeValidators();
        updatedSchema.initializeValidators();

        // validate new json payload to its own schema
        Set<ValidationMessage> validationMessages = updatedSchema.validate(jsonNodeNewVersion);
        Assertions.assertTrue(validationMessages.isEmpty());

        // check for backward compatibility to its original/old schema
        // should return list of error
        Set<ValidationMessage> validationMessages2 = originSchema.validate(jsonNodeNewVersion);
        Assertions.assertFalse(validationMessages2.isEmpty());
    }

    @Test
    public void addDifferentStructureOfAddress() throws IOException{
        JsonSchema originSchema = getJsonSchemaFromClasspath("schema/json/customerCreated-v1.0.0.json");
        JsonSchema updatedSchema = getJsonSchemaFromClasspath("schema/json/customerCreated-v1.4.0.json");

        JsonNode jsonNodeNewVersion = getJsonNodeFromClasspath("events/customerCreated-event-1.4.0.json");

        originSchema.initializeValidators();
        updatedSchema.initializeValidators();

        // validate new json payload to its own schema
        Set<ValidationMessage> validationMessages = updatedSchema.validate(jsonNodeNewVersion);
        Assertions.assertTrue(validationMessages.isEmpty());

        // check for backward compatibility to its original/old schema
        // this should pass, but we need to call business validator in contract test later
        Set<ValidationMessage> validationMessages2 = originSchema.validate(jsonNodeNewVersion);
        Assertions.assertTrue(validationMessages2.isEmpty());
    }
        
    
}
