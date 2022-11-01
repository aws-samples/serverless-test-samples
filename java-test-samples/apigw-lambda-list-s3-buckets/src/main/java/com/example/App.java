/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: MIT-0
 */

package com.example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import software.amazon.awssdk.awscore.exception.AwsServiceException;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.Bucket;

import java.util.HashMap;
import java.util.Map;

import static java.util.stream.Collectors.joining;

public class App implements RequestHandler<APIGatewayProxyRequestEvent, APIGatewayProxyResponseEvent> {
  private final S3Client s3client;

  public App() {
    this(null);
  }

  public App(S3Client s3Client) {
    s3client = s3Client != null ? s3Client : S3Client.builder()
      .region(Region.of(System.getenv("AWS_REGION")))
      .httpClient(ApacheHttpClient.create())
      .build();
  }

  public APIGatewayProxyResponseEvent handleRequest(final APIGatewayProxyRequestEvent input, final Context context) {
    Map<String, String> headers = new HashMap<>();
    headers.put("Content-Type", "text/plain");

    APIGatewayProxyResponseEvent response = new APIGatewayProxyResponseEvent()
      .withHeaders(headers);

    try {
      String output = s3client.listBuckets().buckets().stream()
        .map(Bucket::name)
        .collect(joining("|"));

      return response
        .withStatusCode(200)
        .withBody(output);
    } catch (AwsServiceException e) {
      e.printStackTrace();
      return response
        .withBody("{}")
        .withStatusCode(500);
    }
  }
}
