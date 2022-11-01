/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: MIT-0
 */

package com.example;

import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import com.amazonaws.services.lambda.runtime.tests.annotations.Event;
import com.example.model.Ticket;
import com.example.utils.DDBUtils;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.params.ParameterizedTest;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.MockitoAnnotations;

import java.util.UUID;

//This is a Unit test that uses Mockito to mock calls to AWS services
public class TicketFunctionMockTest {

    @Mock
    private transient DDBUtils testUtils;
    private transient String uuid = null;
    private TicketFunction function = new TicketFunction();

    @BeforeEach
    public void beforeEach() {
        MockitoAnnotations.openMocks(this);
        uuid = UUID.randomUUID().toString();
        Mockito.when(testUtils.persistTicket(Mockito.any(Ticket.class))).thenReturn(uuid);
        //Uses reflection for setting field with no setter
        try {
            TicketFunction.class.getDeclaredField("ddbUtils").set(function, testUtils);
        } catch (Exception e) {
            e.printStackTrace();
            Assertions.fail();
        }
    }

    @ParameterizedTest
    @Event(value = "events/apigw_request_1.json", type = APIGatewayProxyRequestEvent.class)
    public void testEventDeserialization(APIGatewayProxyRequestEvent event) {
        try {
            APIGatewayProxyResponseEvent response = function.handleRequest(event, null);
            ArgumentCaptor<Ticket> ticketArgumentCaptor = ArgumentCaptor.forClass(Ticket.class);
            Mockito.verify(testUtils).persistTicket(ticketArgumentCaptor.capture());
            Assertions.assertEquals("Lambda rocks", ticketArgumentCaptor.getValue().getDescription());
            Assertions.assertEquals("testuser", ticketArgumentCaptor.getValue().getUserId());
        } catch (Exception e) {
            e.printStackTrace();
            Assertions.fail();
        }
    }

    @ParameterizedTest
    @Event(value = "events/apigw_request_1.json", type = APIGatewayProxyRequestEvent.class)
    public void testPutTicketWithEvent(APIGatewayProxyRequestEvent event) {
        try {
            APIGatewayProxyResponseEvent response = function.handleRequest(event, null);
            Assertions.assertNotNull(response);
            Assertions.assertNotNull(response.getBody());
            Assertions.assertEquals(response.getBody(), "\"" + uuid + "\"");

        } catch (Exception e) {
            e.printStackTrace();
            Assertions.fail();
        }
    }

    @ParameterizedTest
    @Event(value = "events/apigw_request_nobody.json", type = APIGatewayProxyRequestEvent.class)
    public void testPutTicketWithBadEvent(APIGatewayProxyRequestEvent event) {
        try {
            APIGatewayProxyResponseEvent response = function.handleRequest(event, null);
            Assertions.assertNotNull(response);
            Assertions.assertNull(response.getBody());
        } catch (Exception e) {
            e.printStackTrace();
            Assertions.fail();
        }
    }

}
