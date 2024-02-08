package com.amazon.aws.sample.mapper;

import com.amazon.aws.sample.model.Customer;
import com.amazon.aws.sample.model.CustomerView;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class CustomerMapperTest {

    private static final String customerId = "1";
    private static final String name = "customer-1";
    private static final String email = "customer1@gmail.com";

    @Test
    public void convertToCustomer_shouldConvertCustomerViewToCustomer() {
        // Arrange
        CustomerView customerView = new CustomerView();
        customerView.setCustomerId(customerId);
        customerView.setName(name);
        customerView.setEmail(email);

        // Act
        Customer customer = new CustomerMapper().convertToCustomer(customerView);

        // Assert
        assertEquals(customerId, customer.getCustomerId());
        assertEquals(name, customer.getName());
        assertEquals(email, customer.getEmail());
    }
}
