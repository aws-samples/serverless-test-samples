package com.amazon.aws.sample.controller;

import com.amazon.aws.sample.mapper.CustomerMapper;
import com.amazon.aws.sample.model.Customer;
import com.amazon.aws.sample.model.CustomerView;
import com.amazon.aws.sample.service.CustomerServiceImpl;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.core.io.ClassPathResource;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;
import org.springframework.test.web.servlet.result.MockMvcResultMatchers;
import org.springframework.util.StreamUtils;

import java.util.Collections;
import java.util.List;

import static java.nio.charset.Charset.defaultCharset;
import static org.junit.Assert.assertEquals;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;


@WebMvcTest(CustomerController.class)
class CustomerControllerTest {

    @Autowired
    MockMvc mockMvc;
    @Mock
    CustomerServiceImpl customerService;
    @Mock
    CustomerMapper mapper;

    @InjectMocks
    CustomerController customerController;

    private static final String customerId = "1";
    private static final String name = "customer-1";
    private static final String email = "customer1@gmail.com";

    //test to retrieve all customers
    @Test
    public void getAllCustomersTest() throws Exception {
        String input = StreamUtils.copyToString(
                new ClassPathResource("sampleRequest.json").getInputStream(), defaultCharset());
        when(customerService.getAllCustomers()).thenReturn(Collections.emptyList());
        List<Customer> customer = customerService.getAllCustomers();
        mockMvc.perform(MockMvcRequestBuilders.get("/customers/all")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(MockMvcResultMatchers.content().json(input));

        verify(customerService, times(1)).getAllCustomers();
    }

    // test to retrieve customers using customer-id
    @Test
    void getCustomerTest() throws Exception {

        Customer customer = customerService.getCustomer(customerId);
        when(customerService.getCustomer(customerId)).thenReturn(customer);

        mockMvc.perform(MockMvcRequestBuilders.get("/customers?customerId={customerId}", customerId)
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(MockMvcResultMatchers.status().isOk())
                .andExpect(MockMvcResultMatchers.jsonPath("$.customerId").value(customerId))
                .andExpect(MockMvcResultMatchers.jsonPath("$.name").value(name))
                .andExpect(MockMvcResultMatchers.jsonPath("$.email").value(email));

        verify(customerService, times(1)).getCustomer(customerId);
    }

    // test to add customer
    @Test
    void insertCustomerTest() {
        // Create a mock customer view
        CustomerView customerView = new CustomerView();
        customerView.setCustomerId(customerId);
        customerView.setName(name);
        customerView.setEmail(email);

        // Create a mock customer
        Customer customer = new Customer();
        customer.setCustomerId(customerId);
        customer.setName(name);
        customer.setEmail(email);

        // Mock the behavior of the DynamoDBMapper
        Mockito.when(mapper.convertToCustomer(customerView)).thenReturn(customer);
        Mockito.when(customerService.save(customer)).thenReturn(customer);

        // Call the insertCustomer method
        Customer savedCustomer = customerController.insertCustomer(customerView);

        // Verify that the DynamoDBMapper was called to convert the customer view to a customer
        Mockito.verify(mapper, times(1)).convertToCustomer(customerView);

        // Verify that the customer service was called to save the customer
        Mockito.verify(customerService, times(1)).save(customer);

        // Assert that the saved customer is the same as the mocked customer
        assertEquals(savedCustomer, customer);
    }

    @Test
    public void deleteCustomerTest() {
        customerController.deleteCustomer(customerId);
        verify(customerService, times(1)).deleteCustomer(customerId);
        assertEquals("customer deleted!!", customerController.deleteCustomer(customerId));
    }
}

