/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: MIT-0
 */

package com.example;

import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import com.amazonaws.services.lambda.runtime.tests.annotations.Event;
import org.apache.http.HttpStatus;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.extension.ExtendWith;
import org.junit.jupiter.params.ParameterizedTest;
import org.mockito.junit.jupiter.MockitoExtension;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.Bucket;
import software.amazon.awssdk.services.s3.model.ListBucketsResponse;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class AppWithMockTest {
  private static S3Client s3Client;

  @BeforeEach
  public void setup() {
    s3Client = mock(S3Client.class);
    Bucket bucket = mock(Bucket.class);
    when(bucket.name()).thenReturn("foo");
    lenient().when(s3Client.listBuckets()).thenReturn(ListBucketsResponse.builder().buckets(bucket).build());
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
    assertEquals("foo", content);
  }
}
