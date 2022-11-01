/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: MIT-0
 */

package com.example;

import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
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

  @Test
  public void successfulResponse() {
    App app = new App(s3Client);
    APIGatewayProxyResponseEvent result = app.handleRequest(null, null);
    assertEquals(200, result.getStatusCode().intValue());
    assertEquals("text/plain", result.getHeaders().get("Content-Type"));
    String content = result.getBody();
    assertNotNull(content);
    assertTrue(content.length() > 0);
    assertEquals("foo", content);
  }
}
