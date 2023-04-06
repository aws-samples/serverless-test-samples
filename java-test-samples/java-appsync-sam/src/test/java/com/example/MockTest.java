package com.example;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Map;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import software.amazon.awssdk.services.appsync.AppSyncClient;
import software.amazon.awssdk.services.appsync.model.EvaluateMappingTemplateRequest;
import software.amazon.awssdk.services.appsync.model.EvaluateMappingTemplateResponse;

public class MockTest {

    private static String locationContext = "{\"arguments\":\n    {\n        \"locationid\": \"1234567890\",\n        \"name\": \"Location Name\",\n        \"description\": \"Location Description\",\n        \"imageUrl\": \"https://www.example.com/image.jpg\"\n    },\n\"result\": {\n    \"locationid\": \"1234567890\",\n    \"imageUrl\": \"https://www.example.com/image.jpg\",\n    \"name\": \"Location Name\",\n    \"description\": \"Location Description\",\n    \"timestamp\": \"2023-01-01T00:00:00.000Z\"\n}}";
    private static String resourceContext = "{\n        \"arguments\":\n            {\n                \"resourceid\": \"1234567890\",\n                \"locationid\": \"abcdefghij\",\n                \"name\": \"Resource Name\",\n                \"description\": \"Resource Description\",\n                \"type\": \"Resource Type\"\n            },\n        \"result\":\n            {\n                \"resourceid\": \"1234567890\",\n                \"locationid\": \"abcdefghij\",\n                \"name\": \"Resource Name\",\n                \"description\": \"Resource Description\",\n                \"type\": \"Resource Type\",\n                \"timestamp\": \"2023-01-01T00:00:00.000Z\"\n            }\n    }";
    private static String bookingContext = "{\n        \"arguments\":\n            {\n                \"bookingid\": \"1234567890\",\n                \"resourceid\": \"abcdefghij\"\n            },\n        \"identity\":\n            {\n                \"sub\": \"123456-abcdeefg-7890\",\n                \"issuer\": \"\",\n                \"username\": \"johndoe\",\n                \"claims\": {},\n                \"sourceIp\": [\n                    \"x.x.x.x\"\n                ],\n                \"defaultAuthStrategy\": \"ALLOW\"\n            },\n        \"result\":\n            {\n                \"bookingid\": \"1234567890\",\n                \"resourceid\": \"abcdefghij\",\n                \"starttimeepochtime\": 1672578000,\n                \"userid\": \"123456-abcdeefg-7890\",\n                \"timestamp\": \"2023-01-01T00:00:00.000Z\"\n            }\n    }";

    private AppSyncClient appClient;
    private String currentDir = System.getProperty("user.dir");

    @BeforeEach
    private void beforeEach(){
        try {
            appClient = AppSyncClient.builder().build();
        } catch (Exception e) {
            e.printStackTrace();
        }
        
    }
    
    @Test
    public void testFirst(){
        String testString = "halo";
        Assertions.assertNotNull(testString);
    }

    @Test
    public void testCreateLocationResolverWithLocationId(){
        try {
            ObjectMapper mapper = new ObjectMapper();
            JsonNode contextMap = mapper.readTree(locationContext);

            // Test request mapping template
            EvaluateMappingTemplateRequest templateRequest = EvaluateMappingTemplateRequest.builder()
                .template(getTemplateToString("create_location_request.vtl"))
                .context(locationContext)
                .build();
            EvaluateMappingTemplateResponse templateResponseRequest = appClient.evaluateMappingTemplate(templateRequest);
            Assertions.assertNotNull(templateResponseRequest.evaluationResult());
            
            JsonNode resultMapRequest = mapper.readTree(templateResponseRequest.evaluationResult());
            
            Assertions.assertEquals("PutItem", resultMapRequest.get("operation").asText());
            Assertions.assertEquals(contextMap.get("arguments").get("locationid"), resultMapRequest.get("key").get("locationid").get("S"));

            // Test response mapping response
            EvaluateMappingTemplateRequest templateResponse = EvaluateMappingTemplateRequest.builder()
                .template(getTemplateToString("create_location_response.vtl"))
                .context(locationContext)
                .build();
            EvaluateMappingTemplateResponse templateResponseResponse = appClient.evaluateMappingTemplate(templateResponse);
            Assertions.assertNotNull(templateResponseResponse.evaluationResult());

            JsonNode resultMapResponse = mapper.readTree(templateResponseResponse.evaluationResult());
            for (JsonNode jsonNode : resultMapResponse) {
                Assertions.assertEquals(contextMap.get("result").get(jsonNode.asText()), resultMapResponse.get(jsonNode.asText()));
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        
    }

    @Test
    public void testGetAllLocationResolver() throws IOException{
        String context = "{\n            \"arguments\":\n                {\n                },\n            \"result\": {\n                    \"items\": [\n                        {\n                            \"locationid\": \"0\",\n                            \"imageUrl\": \"url\",\n                            \"name\": \"name\",\n                            \"description\": \"description\",\n                            \"timestamp\": \"2023-01-01T00:00:00.000Z\"\n                        },\n                        {\n                            \"locationid\": \"2\",\n                            \"imageUrl\": \"url2\",\n                            \"name\": \"name2\",\n                            \"description\": \"description2\",\n                            \"timestamp\": \"2023-01-01T00:00:00.000Z\"\n                        },\n                        {\n                            \"locationid\": \"1\",\n                            \"imageUrl\": \"url1\",\n                            \"name\": \"name1\",\n                            \"description\": \"description1\",\n                            \"timestamp\": \"2023-01-01T00:00:00.000Z\"\n                        }\n                    ],\n                    \"scannedCount\": 3\n            }\n        }";
        ObjectMapper mapper = new ObjectMapper();
        JsonNode contextMap = mapper.readTree(context);
        JsonNode contextMapItems = contextMap.get("result").get("items");
        // Test request mapping template
        EvaluateMappingTemplateRequest templateRequest = EvaluateMappingTemplateRequest.builder()
            .template(getTemplateToString("get_locations_request.vtl"))
            .context(context)
            .build();
        EvaluateMappingTemplateResponse templateResponseRequest = appClient.evaluateMappingTemplate(templateRequest);
        Assertions.assertNotNull(templateResponseRequest.evaluationResult());
        
        JsonNode resultMapRequest = mapper.readTree(templateResponseRequest.evaluationResult());
        Assertions.assertEquals("Scan", resultMapRequest.get("operation").asText());

        // Test response mapping response
        EvaluateMappingTemplateRequest templateResponse = EvaluateMappingTemplateRequest.builder()
            .template(getTemplateToString("get_locations_response.vtl"))
            .context(context)
            .build();
        EvaluateMappingTemplateResponse templateResponseResponse = appClient.evaluateMappingTemplate(templateResponse);
        Assertions.assertNotNull(templateResponseResponse.evaluationResult());

        JsonNode resultMapResponse = mapper.readTree(templateResponseResponse.evaluationResult());
        int i=0;
        for (JsonNode jsonNode : resultMapResponse) {
            Assertions.assertEquals(contextMapItems.get(i).get("locationid").asText(), jsonNode.get("locationid").asText());
            i++;
        }
        
    }

    @Test
    public void testCreateResourceResolverWithResourceId() throws IOException{
        ObjectMapper mapper = new ObjectMapper();
        JsonNode contextMap = mapper.readTree(resourceContext);

        // Test request mapping template
        EvaluateMappingTemplateRequest templateRequest = EvaluateMappingTemplateRequest.builder()
            .template(getTemplateToString("create_resource_request.vtl"))
            .context(resourceContext)
            .build();
        EvaluateMappingTemplateResponse templateResponseRequest = appClient.evaluateMappingTemplate(templateRequest);
        Assertions.assertNotNull(templateResponseRequest.evaluationResult());
        
        JsonNode resultMapRequest = mapper.readTree(templateResponseRequest.evaluationResult());
        
        Assertions.assertEquals("PutItem", resultMapRequest.get("operation").asText());
        Assertions.assertEquals(contextMap.get("arguments").get("resourceid"), resultMapRequest.get("key").get("resourceid").get("S"));
        Assertions.assertEquals(contextMap.get("arguments").get("locationid"), resultMapRequest.get("attributeValues").get("locationid").get("S"));
        Assertions.assertEquals(contextMap.get("arguments").get("name"), resultMapRequest.get("attributeValues").get("name").get("S"));
        Assertions.assertEquals(contextMap.get("arguments").get("description"), resultMapRequest.get("attributeValues").get("description").get("S"));
        Assertions.assertEquals(contextMap.get("arguments").get("type"), resultMapRequest.get("attributeValues").get("type").get("S"));
        Assertions.assertNotNull(resultMapRequest.get("attributeValues").get("timestamp").get("S"));

        // Test response mapping response
        EvaluateMappingTemplateRequest templateResponse = EvaluateMappingTemplateRequest.builder()
            .template(getTemplateToString("create_resource_response.vtl"))
            .context(locationContext)
            .build();
        EvaluateMappingTemplateResponse templateResponseResponse = appClient.evaluateMappingTemplate(templateResponse);
        Assertions.assertNotNull(templateResponseResponse.evaluationResult());

        JsonNode resultMapResponse = mapper.readTree(templateResponseResponse.evaluationResult());
        for (JsonNode jsonNode : resultMapResponse) {
            Assertions.assertEquals(contextMap.get("result").get(jsonNode.asText()), resultMapResponse.get(jsonNode.asText()));
        }
    }

    @Test
    public void testCreateResourceResolverWithoutResourceId() throws IOException{
        ObjectMapper mapper = new ObjectMapper();
        JsonNode contextMap = mapper.readTree(resourceContext);

        // Test request mapping template
        EvaluateMappingTemplateRequest templateRequest = EvaluateMappingTemplateRequest.builder()
            .template(getTemplateToString("create_resource_request.vtl"))
            .context(resourceContext)
            .build();
        EvaluateMappingTemplateResponse templateResponseRequest = appClient.evaluateMappingTemplate(templateRequest);
        Assertions.assertNotNull(templateResponseRequest.evaluationResult());
        
        JsonNode resultMapRequest = mapper.readTree(templateResponseRequest.evaluationResult());
        
        Assertions.assertEquals("PutItem", resultMapRequest.get("operation").asText());
        Assertions.assertNotNull(resultMapRequest.get("key").get("resourceid").get("S"));
        Assertions.assertEquals(contextMap.get("arguments").get("locationid"), resultMapRequest.get("attributeValues").get("locationid").get("S"));
        Assertions.assertEquals(contextMap.get("arguments").get("name"), resultMapRequest.get("attributeValues").get("name").get("S"));
        Assertions.assertEquals(contextMap.get("arguments").get("description"), resultMapRequest.get("attributeValues").get("description").get("S"));
        Assertions.assertEquals(contextMap.get("arguments").get("type"), resultMapRequest.get("attributeValues").get("type").get("S"));
        Assertions.assertNotNull(resultMapRequest.get("attributeValues").get("timestamp").get("S"));

        // Test response mapping response
        EvaluateMappingTemplateRequest templateResponse = EvaluateMappingTemplateRequest.builder()
            .template(getTemplateToString("create_resource_response.vtl"))
            .context(locationContext)
            .build();
        EvaluateMappingTemplateResponse templateResponseResponse = appClient.evaluateMappingTemplate(templateResponse);
        Assertions.assertNotNull(templateResponseResponse.evaluationResult());

        JsonNode resultMapResponse = mapper.readTree(templateResponseResponse.evaluationResult());
        for (JsonNode jsonNode : resultMapResponse) {
            Assertions.assertEquals(contextMap.get("result").get(jsonNode.asText()), resultMapResponse.get(jsonNode.asText()));
        }
    }

    @Test
    public void testDeleteLocationResolver() throws IOException {
        ObjectMapper mapper = new ObjectMapper();
        JsonNode contextMap = mapper.readTree(locationContext);

        // Test request mapping template
        EvaluateMappingTemplateRequest templateRequest = EvaluateMappingTemplateRequest.builder()
            .template(getTemplateToString("delete_location_request.vtl"))
            .context(locationContext)
            .build();
        EvaluateMappingTemplateResponse templateResponseRequest = appClient.evaluateMappingTemplate(templateRequest);
        Assertions.assertNotNull(templateResponseRequest.evaluationResult());
        
        JsonNode resultMapRequest = mapper.readTree(templateResponseRequest.evaluationResult());
        
        Assertions.assertEquals("DeleteItem", resultMapRequest.get("operation").asText());
        Assertions.assertEquals(contextMap.get("arguments").get("locationid"), resultMapRequest.get("key").get("locationid").get("S"));

        // Test response mapping response
        EvaluateMappingTemplateRequest templateResponse = EvaluateMappingTemplateRequest.builder()
            .template(getTemplateToString("delete_location_response.vtl"))
            .context(locationContext)
            .build();
        EvaluateMappingTemplateResponse templateResponseResponse = appClient.evaluateMappingTemplate(templateResponse);
        Assertions.assertNotNull(templateResponseResponse.evaluationResult());

        JsonNode resultMapResponse = mapper.readTree(templateResponseResponse.evaluationResult());
        for (JsonNode jsonNode : resultMapResponse) {
            Assertions.assertEquals(contextMap.get("result").get(jsonNode.asText()), resultMapResponse.get(jsonNode.asText()));
        }
    }

    @Test
    public void testGetSingleResourceResolver() throws IOException{
        ObjectMapper mapper = new ObjectMapper();
        JsonNode contextMap = mapper.readTree(resourceContext);

        // Test request mapping template
        EvaluateMappingTemplateRequest templateRequest = EvaluateMappingTemplateRequest.builder()
            .template(getTemplateToString("get_resource_request.vtl"))
            .context(resourceContext)
            .build();
        EvaluateMappingTemplateResponse templateResponseRequest = appClient.evaluateMappingTemplate(templateRequest);
        Assertions.assertNotNull(templateResponseRequest.evaluationResult());
        
        JsonNode resultMapRequest = mapper.readTree(templateResponseRequest.evaluationResult());
        Assertions.assertEquals("GetItem", resultMapRequest.get("operation").asText());
        Assertions.assertEquals(contextMap.get("arguments").get("resourceid"), resultMapRequest.get("key").get("resourceid").get("S"));

        // Test response mapping response
        EvaluateMappingTemplateRequest templateResponse = EvaluateMappingTemplateRequest.builder()
            .template(getTemplateToString("get_resource_response.vtl"))
            .context(resourceContext)
            .build();
        EvaluateMappingTemplateResponse templateResponseResponse = appClient.evaluateMappingTemplate(templateResponse);
        Assertions.assertNotNull(templateResponseResponse.evaluationResult());

        JsonNode resultMapResponse = mapper.readTree(templateResponseResponse.evaluationResult());
        for (JsonNode jsonNode : resultMapResponse) {
            Assertions.assertEquals(contextMap.get("result").get(jsonNode.asText()), resultMapResponse.get(jsonNode.asText()));
        }
    }

    @Test
    public void testGetResourceForLocationResolver() throws IOException {
        String context = "{\n            \"arguments\":\n                {\n                    \"locationid\": \"abcdefghij\"\n                },\n            \"result\": {\n                    \"items\": [\n                        {\n                            \"resourceid\": \"0\",\n                            \"locationid\": \"abcdefghij\",\n                            \"name\": \"Resource Name 0\",\n                            \"description\": \"Resource Description 0\",\n                            \"type\": \"Resource Type 0\",\n                            \"timestamp\": \"2023-01-01T00:00:00.000Z\"\n                        },\n                        {\n                            \"resourceid\": \"1\",\n                            \"locationid\": \"abcdefghij\",\n                            \"name\": \"Resource Name 1\",\n                            \"description\": \"Resource Description 1\",\n                            \"type\": \"Resource Type 1\",\n                            \"timestamp\": \"2023-01-01T00:00:00.000Z\"\n                        }\n                    ],\n                    \"scannedCount\": 2\n            }\n        }";
        ObjectMapper mapper = new ObjectMapper();
        JsonNode contextMap = mapper.readTree(context);
        JsonNode contextMapItems = contextMap.get("result").get("items");
        System.out.println("contextMapItems " + contextMapItems);

        // Test request mapping template
        EvaluateMappingTemplateRequest templateRequest = EvaluateMappingTemplateRequest.builder()
            .template(getTemplateToString("get_resources_for_location_request.vtl"))
            .context(context)
            .build();
        EvaluateMappingTemplateResponse templateResponseRequest = appClient.evaluateMappingTemplate(templateRequest);
        Assertions.assertNotNull(templateResponseRequest.evaluationResult());
        
        JsonNode resultMapRequest = mapper.readTree(templateResponseRequest.evaluationResult());
        Assertions.assertEquals("Query", resultMapRequest.get("operation").asText());
        Assertions.assertEquals("locationid = :locationid", resultMapRequest.get("query").get("expression").asText());
        Assertions.assertEquals(contextMap.get("arguments").get("locationid").asText(), resultMapRequest.get("query").get("expressionValues").get(":locationid").get("S").asText());
        Assertions.assertEquals("locationidGSI", resultMapRequest.get("index").asText());

        // Test response mapping response
        EvaluateMappingTemplateRequest templateResponse = EvaluateMappingTemplateRequest.builder()
            .template(getTemplateToString("get_resources_for_location_response.vtl"))
            .context(context)
            .build();
        EvaluateMappingTemplateResponse templateResponseResponse = appClient.evaluateMappingTemplate(templateResponse);
        Assertions.assertNotNull(templateResponseResponse.evaluationResult());

        JsonNode resultMapResponse = mapper.readTree(templateResponseResponse.evaluationResult());
        System.out.println("resultMap " + resultMapResponse);
        int i=0;
        for (JsonNode jsonNode : resultMapResponse) {
            Assertions.assertEquals(contextMapItems.get(i).get("locationid").asText(), jsonNode.get("locationid").asText());
            Assertions.assertEquals(contextMapItems.get(i).get("resourceid").asText(), jsonNode.get("resourceid").asText());
            Assertions.assertEquals(contextMapItems.get(i).get("name").asText(), jsonNode.get("name").asText());
            Assertions.assertEquals(contextMapItems.get(i).get("description").asText(), jsonNode.get("description").asText());
            Assertions.assertEquals(contextMapItems.get(i).get("type").asText(), jsonNode.get("type").asText());
            Assertions.assertEquals(contextMapItems.get(i).get("timestamp").asText(), jsonNode.get("timestamp").asText());
            i++;
        }
    }

    @Test
    public void testCreateBookingResolverWithBookingId() throws IOException {
        ObjectMapper mapper = new ObjectMapper();
        JsonNode contextMap = mapper.readTree(bookingContext);

        // Test request mapping template
        EvaluateMappingTemplateRequest templateRequest = EvaluateMappingTemplateRequest.builder()
            .template(getTemplateToString("create_booking_request.vtl"))
            .context(bookingContext)
            .build();
        EvaluateMappingTemplateResponse templateResponseRequest = appClient.evaluateMappingTemplate(templateRequest);
        Assertions.assertNotNull(templateResponseRequest.evaluationResult());
        
        JsonNode resultMapRequest = mapper.readTree(templateResponseRequest.evaluationResult());
        
        Assertions.assertEquals("PutItem", resultMapRequest.get("operation").asText());
        Assertions.assertEquals(contextMap.get("arguments").get("bookingid"), resultMapRequest.get("key").get("bookingid").get("S"));
        Assertions.assertEquals(contextMap.get("arguments").get("resourceid"), resultMapRequest.get("attributeValues").get("resourceid").get("S"));
        Assertions.assertEquals(contextMap.get("identity").get("sub"), resultMapRequest.get("attributeValues").get("userid").get("S"));
        Assertions.assertNotNull(resultMapRequest.get("attributeValues").get("timestamp").get("S"));

        // Test response mapping response
        EvaluateMappingTemplateRequest templateResponse = EvaluateMappingTemplateRequest.builder()
            .template(getTemplateToString("create_booking_request.vtl"))
            .context(bookingContext)
            .build();
        EvaluateMappingTemplateResponse templateResponseResponse = appClient.evaluateMappingTemplate(templateResponse);
        Assertions.assertNotNull(templateResponseResponse.evaluationResult());

        JsonNode resultMapResponse = mapper.readTree(templateResponseResponse.evaluationResult());
        for (JsonNode jsonNode : resultMapResponse) {
            Assertions.assertEquals(contextMap.get("result").get(jsonNode.asText()), resultMapResponse.get(jsonNode.asText()));
        }
    }

    @Test
    public void testCreateBookingResolverWithoutBookingId() throws IOException {
        String context = "{\n        \"arguments\":\n            {\n                \"resourceid\": \"abcdefghij\"\n            },\n        \"identity\":\n            {\n                \"sub\": \"123456-abcdeefg-7890\",\n                \"issuer\": \"\",\n                \"username\": \"johndoe\",\n                \"claims\": {},\n                \"sourceIp\": [\n                    \"x.x.x.x\"\n                ],\n                \"defaultAuthStrategy\": \"ALLOW\"\n            },\n        \"result\":\n            {\n                \"bookingid\": \"1234567890\",\n                \"resourceid\": \"abcdefghij\",\n                \"starttimeepochtime\": 1672578000,\n                \"userid\": \"123456-abcdeefg-7890\",\n                \"timestamp\": \"2023-01-01T00:00:00.000Z\"\n            }\n    }";
        ObjectMapper mapper = new ObjectMapper();
        JsonNode contextMap = mapper.readTree(context);

        // Test request mapping template
        EvaluateMappingTemplateRequest templateRequest = EvaluateMappingTemplateRequest.builder()
            .template(getTemplateToString("create_booking_request.vtl"))
            .context(context)
            .build();
        EvaluateMappingTemplateResponse templateResponseRequest = appClient.evaluateMappingTemplate(templateRequest);
        Assertions.assertNotNull(templateResponseRequest.evaluationResult());
        
        JsonNode resultMapRequest = mapper.readTree(templateResponseRequest.evaluationResult());
        
        Assertions.assertEquals("PutItem", resultMapRequest.get("operation").asText());
        Assertions.assertNotNull(resultMapRequest.get("key").get("bookingid").get("S"));
        Assertions.assertEquals(contextMap.get("arguments").get("resourceid"), resultMapRequest.get("attributeValues").get("resourceid").get("S"));
        Assertions.assertEquals(contextMap.get("identity").get("sub"), resultMapRequest.get("attributeValues").get("userid").get("S"));
        Assertions.assertNotNull(resultMapRequest.get("attributeValues").get("timestamp").get("S"));

        // Test response mapping response
        EvaluateMappingTemplateRequest templateResponse = EvaluateMappingTemplateRequest.builder()
            .template(getTemplateToString("create_booking_request.vtl"))
            .context(context)
            .build();
        EvaluateMappingTemplateResponse templateResponseResponse = appClient.evaluateMappingTemplate(templateResponse);
        Assertions.assertNotNull(templateResponseResponse.evaluationResult());

        JsonNode resultMapResponse = mapper.readTree(templateResponseResponse.evaluationResult());
        for (JsonNode jsonNode : resultMapResponse) {
            Assertions.assertEquals(contextMap.get("result").get(jsonNode.asText()), resultMapResponse.get(jsonNode.asText()));
        }
    }

    @Test
    public void testGetSingleBookingResolver() throws IOException {
        ObjectMapper mapper = new ObjectMapper();
        JsonNode contextMap = mapper.readTree(bookingContext);

        // Test request mapping template
        EvaluateMappingTemplateRequest templateRequest = EvaluateMappingTemplateRequest.builder()
            .template(getTemplateToString("get_booking_request.vtl"))
            .context(bookingContext)
            .build();
        EvaluateMappingTemplateResponse templateResponseRequest = appClient.evaluateMappingTemplate(templateRequest);
        Assertions.assertNotNull(templateResponseRequest.evaluationResult());
        
        JsonNode resultMapRequest = mapper.readTree(templateResponseRequest.evaluationResult());
        
        Assertions.assertEquals("GetItem", resultMapRequest.get("operation").asText());
        Assertions.assertEquals(contextMap.get("arguments").get("bookingid"), resultMapRequest.get("key").get("bookingid").get("S"));
        
        // Test response mapping response
        EvaluateMappingTemplateRequest templateResponse = EvaluateMappingTemplateRequest.builder()
            .template(getTemplateToString("get_booking_response.vtl"))
            .context(bookingContext)
            .build();
        EvaluateMappingTemplateResponse templateResponseResponse = appClient.evaluateMappingTemplate(templateResponse);
        Assertions.assertNotNull(templateResponseResponse.evaluationResult());

        JsonNode resultMapResponse = mapper.readTree(templateResponseResponse.evaluationResult());
        for (JsonNode jsonNode : resultMapResponse) {
            Assertions.assertEquals(contextMap.get("result").get(jsonNode.asText()), resultMapResponse.get(jsonNode.asText()));
        }
    }

    @Test
    public void testGetBookingsForResourceResolver() throws IOException{

    }

    private String getTemplateToString(String location) throws IOException{

        try {
            Path path = Paths.get(currentDir,"src","mapping_templates",location);
            String content = new String(Files.readAllBytes(path));
            return content;
        } catch (IOException e) {
            throw e;
        }
        
    }
}
