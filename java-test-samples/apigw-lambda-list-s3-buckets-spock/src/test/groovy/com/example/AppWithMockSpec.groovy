package com.example


import groovy.json.JsonSlurper
import software.amazon.awssdk.services.s3.S3Client
import spock.lang.Specification

import static com.example.fixtures.ApiGwRequestFixtures.*
import static com.example.fixtures.BucketFixtures.TEST_BUCKET_NAME
import static com.example.fixtures.BucketFixtures.listWithBucket

class AppWithMockSpec  extends Specification {


    def mockS3Client = Mock(S3Client)
    def app = new App(mockS3Client)

    def "returns a list of buckets"() {
        given: "a bucket exists"
        1 * mockS3Client.listBuckets() >> listWithBucket()

        when: "a request is received"
        def request =  getRequestFromFile()
        def responseEvent = app.handleRequest(request, null)

        then: "a list of buckets is returned"
        def responseBody = new JsonSlurper().parseText(responseEvent.getBody()) as List
        responseBody.size() >= 1

        and: "the first item is the example bucket"
        responseBody.first() == TEST_BUCKET_NAME
    }
}
