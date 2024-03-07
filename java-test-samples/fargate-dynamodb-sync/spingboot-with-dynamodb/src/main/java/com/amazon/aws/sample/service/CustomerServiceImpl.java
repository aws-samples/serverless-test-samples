package com.amazon.aws.sample.service;

import com.amazon.aws.sample.dao.CustomerDao;
import com.amazon.aws.sample.model.Customer;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class CustomerServiceImpl implements CustomerService {

    @Autowired
    private CustomerDao customerDao;

    /**
     * @param customer
     * @return save customer data as provided
     */
    @Override
    public Customer save(Customer customer) {
        return customerDao.save(customer);
    }

    /**
     * @param id
     * @return customer details based on customer-id
     */
    @Override
    public Customer getCustomer(String id) {
        return customerDao.getCustomer(id);
    }

    /**
     * @return details of all customers
     */
    @Override
    public List<Customer> getAllCustomers() {
        List<Customer> customers = customerDao.getAllCustomers();
        return customers;
    }

    /**
     * @param customerId delete customer details based on customer-id
     */
    public void deleteCustomer(String customerId) {
        customerDao.deleteCustomer(customerId);
    }
}
