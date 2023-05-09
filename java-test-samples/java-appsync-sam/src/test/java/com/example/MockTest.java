package com.example;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import software.amazon.awssdk.services.appsync.AppSyncClient;
import software.amazon.awssdk.services.appsync.model.EvaluateMappingTemplateRequest;
import software.amazon.awssdk.services.appsync.model.EvaluateMappingTemplateResponse;

public class MockTest {

    private static String locationContext = """
        {
            "arguments":
                {
                    "locationid": "1234567890",
                    "name": "Location Name",
                    "description": "Location Description",
                    "imageUrl": "https://www.example.com/image.jpg"
                },
            "result": {
                "locationid": "1234567890",
                "imageUrl": "https://www.example.com/image.jpg",
                "name": "Location Name",
                "description": "Location Description",
                "timestamp": "2023-01-01T00:00:00.000Z"
            }
        }
            """;
    private static String resourceContext = """
        {
            "arguments":
                {
                    "resourceid": "1234567890",
                    "locationid": "abcdefghij",
                    "name": "Resource Name",
                    "description": "Resource Description",
                    "type": "Resource Type"
                },
            "result":
                {
                    "resourceid": "1234567890",
                    "locationid": "abcdefghij",
                    "name": "Resource Name",
                    "description": "Resource Description",
                    "type": "Resource Type",
                    "timestamp": "2023-01-01T00:00:00.000Z"
                }
        }
            """;
    private static String bookingContext = """
        {
            "arguments":
                {
                    "bookingid": "1234567890",
                    "resourceid": "abcdefghij"
                },
            "identity":
                {
                    "sub": "123456-abcdeefg-7890",
                    "issuer": "",
                    "username": "johndoe",
                    "claims": {},
                    "sourceIp": [
                        "x.x.x.x"
                    ],
                    "defaultAuthStrategy": "ALLOW"
                },
            "result":
                {
                    "bookingid": "1234567890",
                    "resourceid": "abcdefghij",
                    "starttimeepochtime": 1672578000,
                    "userid": "123456-abcdeefg-7890",
                    "timestamp": "2023-01-01T00:00:00.000Z"
                }
        }
            """;

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
        String context = """
            {
                "arguments":
                    {
                    },
                "result": {
                        "items": [
                            {
                                "locationid": "0",
                                "imageUrl": "url",
                                "name": "name",
                                "description": "description",
                                "timestamp": "2023-01-01T00:00:00.000Z"
                            },
                            {
                                "locationid": "2",
                                "imageUrl": "url2",
                                "name": "name2",
                                "description": "description2",
                                "timestamp": "2023-01-01T00:00:00.000Z"
                            },
                            {
                                "locationid": "1",
                                "imageUrl": "url1",
                                "name": "name1",
                                "description": "description1",
                                "timestamp": "2023-01-01T00:00:00.000Z"
                            }
                        ],
                        "scannedCount": 3
                }
            }
                """;
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
        String context = """
            {
                "arguments":
                    {
                        "locationid": "abcdefghij"
                    },
                "result": {
                        "items": [
                            {
                                "resourceid": "0",
                                "locationid": "abcdefghij",
                                "name": "Resource Name 0",
                                "description": "Resource Description 0",
                                "type": "Resource Type 0",
                                "timestamp": "2023-01-01T00:00:00.000Z"
                            },
                            {
                                "resourceid": "1",
                                "locationid": "abcdefghij",
                                "name": "Resource Name 1",
                                "description": "Resource Description 1",
                                "type": "Resource Type 1",
                                "timestamp": "2023-01-01T00:00:00.000Z"
                            }
                        ],
                        "scannedCount": 2
                }
            }
                """;
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
        Assertions.assertNotNull(resultMapRequest.get("key").get("bookingid").get("S"));
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
