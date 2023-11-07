/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: MIT-0
 */

package com.example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import com.amazonaws.util.StringUtils;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.http.HttpStatus;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import software.amazon.awssdk.awscore.exception.AwsServiceException;
import software.amazon.awssdk.http.SdkHttpMethod;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.Bucket;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static java.util.stream.Collectors.toList;

public class App implements RequestHandler<APIGatewayProxyRequestEvent, APIGatewayProxyResponseEvent> {

  private static final Logger logger = LoggerFactory.getLogger(App.class);
  private final S3Client s3client;

  private static final ObjectMapper mapper = new ObjectMapper();

  public App() {
    this(null);
  }

  public App(S3Client s3Client) {
    s3client = s3Client != null ? s3Client : S3Client.builder()
      .httpClient(ApacheHttpClient.create())
      .build();
  }

  public APIGatewayProxyResponseEvent handleRequest(final APIGatewayProxyRequestEvent event, final Context context) {
    Map<String, String> headers = new HashMap<>();
    headers.put("Content-Type", "application/json");

    APIGatewayProxyResponseEvent response = new APIGatewayProxyResponseEvent()
      .withHeaders(headers);

    if (notAGetRequest(event)) {
      logger.error("Http Method " + event.getHttpMethod() + " is not supported");
      return httpMethodNotSupportedResponse(response);
    }

    try {
      List<String> listOfBuckets = getListOfBuckets();

      return response
        .withStatusCode(HttpStatus.SC_OK)
        .withBody(mapper.writerWithDefaultPrettyPrinter().writeValueAsString(listOfBuckets));
    } catch (AwsServiceException e) {
      logger.error("AWS Service Exception occurred: ", e);
      return httpInternalServerErrorResponse(response);
    } catch (JsonProcessingException e) {
      logger.error("Json Processing Exception occurred: ", e);
      return httpInternalServerErrorResponse(response);
    }
  }

  private static APIGatewayProxyResponseEvent httpInternalServerErrorResponse(APIGatewayProxyResponseEvent response) {
    return response
      .withBody("{}")
      .withStatusCode(HttpStatus.SC_INTERNAL_SERVER_ERROR);
  }

  private List<String> getListOfBuckets() {
    return s3client.listBuckets().buckets().stream()
      .map(Bucket::name)
      .collect(toList());
  }

  private static APIGatewayProxyResponseEvent httpMethodNotSupportedResponse(APIGatewayProxyResponseEvent response) {
    return response
      .withStatusCode(HttpStatus.SC_METHOD_NOT_ALLOWED)
      .withBody("Http Method Not Supported");
  }

  private static boolean notAGetRequest(APIGatewayProxyRequestEvent event) {
    return !StringUtils.isNullOrEmpty(event.getHttpMethod()) &&
      !SdkHttpMethod.GET.name().equalsIgnoreCase(event.getHttpMethod());
  }
}
