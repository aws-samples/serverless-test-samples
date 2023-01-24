/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: MIT-0
 */

package com.example;

import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import com.amazonaws.services.lambda.runtime.tests.annotations.Event;
import com.amazonaws.xray.AWSXRay;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.http.HttpStatus;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.extension.ExtendWith;
import org.junit.jupiter.params.ParameterizedTest;
import software.amazon.awssdk.auth.credentials.AwsCredentials;
import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import uk.org.webcompere.systemstubs.environment.EnvironmentVariables;
import uk.org.webcompere.systemstubs.jupiter.SystemStub;
import uk.org.webcompere.systemstubs.jupiter.SystemStubsExtension;

import java.io.IOException;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@ExtendWith(SystemStubsExtension.class)
public class AppTest {
  @SystemStub
  private static EnvironmentVariables environmentVariables = new EnvironmentVariables();

  @BeforeEach
  public void setup() {
    ProfileCredentialsProvider credentialsProvider = ProfileCredentialsProvider.create("default");
    AwsCredentials awsCredentials = credentialsProvider.resolveCredentials();
    environmentVariables.set("AWS_REGION", "us-east-1");
    environmentVariables.set("AWS_ACCESS_KEY_ID", awsCredentials.accessKeyId());
    environmentVariables.set("AWS_SECRET_ACCESS_KEY", awsCredentials.secretAccessKey());
  }

  @ParameterizedTest
  @Event(value = "events/apigw_req_s3_buckets_get.json", type = APIGatewayProxyRequestEvent.class)
  public void successfulGetResponse(APIGatewayProxyRequestEvent event, EnvironmentVariables environmentVariables) throws IOException {
    //This line manually adds the X-ray segment
    AWSXRay.beginSegment("S3");
    App app = new App();
    APIGatewayProxyResponseEvent response = app.handleRequest(event, null);
    Assertions.assertNotNull(response);
    assertEquals(HttpStatus.SC_OK, response.getStatusCode().intValue());
    assertEquals("application/json", response.getHeaders().get("Content-Type"));
    List content = new ObjectMapper().readValue(response.getBody(), List.class);
    assertNotNull(content);
    assertTrue(content.size() > 0);
  }

  @ParameterizedTest
  @Event(value = "events/apigw_req_s3_buckets_post.json", type = APIGatewayProxyRequestEvent.class)
  public void methodNotSupportedResponse(APIGatewayProxyRequestEvent event, EnvironmentVariables environmentVariables) {
    App app = new App();
    APIGatewayProxyResponseEvent response = app.handleRequest(event, null);
    Assertions.assertNotNull(response);
    assertEquals(HttpStatus.SC_METHOD_NOT_ALLOWED, response.getStatusCode().intValue());
    String content = response.getBody();
    assertEquals("Http Method Not Supported", content);
  }
}
