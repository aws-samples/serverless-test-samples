package com.amazon.aws.sample.service;

import com.amazon.aws.sample.model.Customer;

import java.util.List;

public interface CustomerService {

    /**
     * @param customer
     * @return save customer data as provided
     */
    Customer save(Customer customer);

    /**
     * @param id
     * @return customer details based on customer-id
     */
    Customer getCustomer(String id);

    /**
     * @return details of all customers
     */
    List<Customer> getAllCustomers();

    /**
     * @param customerId delete customer details based on customer-id
     */
    void deleteCustomer(String customerId);
}
