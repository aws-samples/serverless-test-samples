package com.amazon.aws.sample.mapper;

import com.amazon.aws.sample.model.Customer;
import com.amazon.aws.sample.model.CustomerView;
import org.springframework.stereotype.Service;

@Service
public class CustomerMapper {

    /**
     * @param customerView
     * @return maps the values of customer-view to customer
     */
    public Customer convertToCustomer(CustomerView customerView) {
        Customer customer = new Customer();
        customer.setCustomerId(customerView.getCustomerId());
        customer.setName(customerView.getName());
        customer.setEmail(customerView.getEmail());
        return customer;
    }
}
