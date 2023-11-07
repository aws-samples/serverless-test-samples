package com.example

import groovy.json.JsonSlurper
import spock.lang.Specification

import static com.example.fixtures.ApiGwRequestFixtures.getRequestFromFile

class AppSpecIT extends Specification {

    private static final String BAD_REQUEST_FILE = "events/apigw_req_s3_buckets_post.json"

    def app = new App()

    def "returns a list of buckets"() {
        when: "a request is received"
        def request =  getRequestFromFile()
        def responseEvent = app.handleRequest(request, null)

        then: "a list of buckets is returned"
        def responseBody = new JsonSlurper().parseText(responseEvent.getBody()) as List
        responseBody.size() >= 1
    }

    def "method not supported response"() {
        when: "a request is received"
        def request =  getRequestFromFile(BAD_REQUEST_FILE)
        def responseEvent = app.handleRequest(request, null)

        then: "a method not supported response is returned"
        responseEvent.getStatusCode() == 405
    }
}
