package com.example.fixtures

import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent
import com.fasterxml.jackson.databind.ObjectMapper
import groovy.json.JsonSlurper

class ApiGwRequestFixtures {

    private static String DEFAULT_REQUEST_PAYLOAD_PATH = "events/apigw_req_s3_buckets_get.json"
    private static String TEST_RESOURCES_PATH = "src/test/resources/"

    static def getRequestFromFile(String filePath = DEFAULT_REQUEST_PAYLOAD_PATH) {
        def file = new File(TEST_RESOURCES_PATH + filePath)
        def json = new JsonSlurper().parse(file)
        return json as APIGatewayProxyRequestEvent
    }
}
