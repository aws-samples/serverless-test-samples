package com.amazon.aws.sample.dao;

import com.amazon.aws.sample.model.Customer;
import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBScanExpression;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Repository;
import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBMapper;

import java.util.List;

@Repository
public class CustomerDao {

    private DynamoDBMapper dynamoDBMapper;

    @Autowired
    public CustomerDao(DynamoDBMapper dynamoDBMapper) {
        this.dynamoDBMapper = dynamoDBMapper;
    }

    /**
     * @param id
     * @return customer details based on customer-id
     */
    public Customer getCustomer(String id) {
        return dynamoDBMapper.load(Customer.class, id);
    }

    /**
     * @param id
     * delete customer details based on customer-id
     */
    public void deleteCustomer(String id) {
        Customer customer = dynamoDBMapper.load(Customer.class, id);
        dynamoDBMapper.delete(customer);
    }

    /**
     * @return details of all customers
     */
    public List<Customer> getAllCustomers() {
        return dynamoDBMapper.scan(Customer.class, new DynamoDBScanExpression());
    }

    /**
     * @param customer
     * @return save customer details
     */
    public Customer save(Customer customer) {
        dynamoDBMapper.save(customer);
        return customer;
    }
}
