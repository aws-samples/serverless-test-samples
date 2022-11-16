/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: MIT-0
 */

package com.example;

import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import org.junit.Rule;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.localstack.LocalStackContainer;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.utility.DockerImageName;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;

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

  @Test
  public void successfulResponse() {
    App app = new App(s3Client);
    APIGatewayProxyResponseEvent result = app.handleRequest(null, null);
    assertEquals(200, result.getStatusCode().intValue());
    assertEquals("text/plain", result.getHeaders().get("Content-Type"));
    String content = result.getBody();
    assertNotNull(content);
    assertTrue(content.length() > 0);
    assertEquals("foo|bar", content);
  }
}
