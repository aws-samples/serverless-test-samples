package com.example.fixtures

import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent
import com.fasterxml.jackson.databind.DeserializationFeature
import com.fasterxml.jackson.databind.ObjectMapper

class ApiGwRequestFixtures {

    private static String DEFAULT_REQUEST_PAYLOAD_PATH = "events/apigw_req_s3_buckets_get.json"
    private static String TEST_RESOURCES_PATH = "src/test/resources/"

    static def getRequestFromFile(String filePath = DEFAULT_REQUEST_PAYLOAD_PATH) {
        def file = new File(TEST_RESOURCES_PATH + filePath)
        return new ObjectMapper()
            .disable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES)
            .readValue(file, APIGatewayProxyRequestEvent)
    }
}
