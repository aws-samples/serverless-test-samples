/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: MIT-0
 */

package com.example;

import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import com.amazonaws.services.lambda.runtime.tests.annotations.Event;
import org.apache.http.HttpStatus;
import org.junit.Rule;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.testcontainers.containers.localstack.LocalStackContainer;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.utility.DockerImageName;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import uk.org.webcompere.systemstubs.environment.EnvironmentVariables;

import static org.junit.jupiter.api.Assertions.*;
import static org.testcontainers.containers.localstack.LocalStackContainer.Service.S3;

@Testcontainers
public class AppIntegrationTest {
  private static S3Client s3Client;

  private static final DockerImageName localStackImage =
    DockerImageName.parse("localstack/localstack:1.2.0");

  @Rule
  public static final LocalStackContainer localstack = new LocalStackContainer(localStackImage).withServices(S3);

  @BeforeAll
  static void setup() {
    localstack.start();

    s3Client = S3Client
      .builder()
      .endpointOverride(localstack.getEndpointOverride(LocalStackContainer.Service.S3))
      .credentialsProvider(
        StaticCredentialsProvider.create(
          AwsBasicCredentials.create(localstack.getAccessKey(), localstack.getSecretKey())
        )
      )
      .region(Region.of(localstack.getRegion()))
      .build();

    s3Client.createBucket(b -> b.bucket("foo"));
    s3Client.createBucket(b -> b.bucket("bar"));
  }

  @AfterAll
  static void cleanup() {
    localstack.stop();
  }

  @ParameterizedTest
  @Event(value = "events/apigw_req_s3_buckets_get.json", type = APIGatewayProxyRequestEvent.class)
  public void successfulGetResponse(APIGatewayProxyRequestEvent event) {
    App app = new App(s3Client);
    APIGatewayProxyResponseEvent response = app.handleRequest(event, null);
    Assertions.assertNotNull(response);
    assertEquals(HttpStatus.SC_OK, response.getStatusCode().intValue());
    assertEquals("text/plain", response.getHeaders().get("Content-Type"));
    String content = response.getBody();
    assertNotNull(content);
    assertTrue(content.length() > 0);
    assertEquals("foo|bar", content);
  }

  @ParameterizedTest
  @Event(value = "events/apigw_req_s3_buckets_post.json", type = APIGatewayProxyRequestEvent.class)
  public void methodNotSupportedResponse(APIGatewayProxyRequestEvent event) {
    App app = new App(s3Client);
    APIGatewayProxyResponseEvent response = app.handleRequest(event, null);
    Assertions.assertNotNull(response);
    assertEquals(HttpStatus.SC_METHOD_NOT_ALLOWED, response.getStatusCode().intValue());
    String content = response.getBody();
    assertEquals("Http Method Not Supported", content);
  }

}
