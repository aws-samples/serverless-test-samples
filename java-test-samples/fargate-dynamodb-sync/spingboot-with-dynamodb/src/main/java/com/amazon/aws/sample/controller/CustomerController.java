package com.amazon.aws.sample.controller;

import com.amazon.aws.sample.mapper.CustomerMapper;
import com.amazon.aws.sample.model.CustomerView;
import com.amazon.aws.sample.model.Customer;
import com.amazon.aws.sample.service.CustomerService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;


@RestController
public class CustomerController {

    @Autowired
    CustomerService customerService;
    @Autowired
    CustomerMapper mapper;

    /**
     * @param customerId
     * @return: customer details based on customer-id
     */
    @RequestMapping(value = "/customer", produces = {"application/json"}, method = RequestMethod.GET)
    public Customer getCustomer(@RequestParam String customerId) {
        // retrieves customer details based on customer-id
        return customerService.getCustomer(customerId);
    }

    /**
     *
     * @return All customers
     */
    @RequestMapping(value = "/customers/all", produces = {"application/json"}, method = RequestMethod.GET)
    public List<Customer> listCustomer() {
        // retrieves all customers
        return customerService.getAllCustomers();
    }

    /**
     *
     * @param customerView
     * @return: adds provided customer details
     */
    @RequestMapping(value = "/customer/new", produces = {"application/json"}, consumes = {"application/json"}, method = RequestMethod.POST)
    public Customer insertCustomer(@RequestBody CustomerView customerView) {
        Customer customer = mapper.convertToCustomer(customerView);
        // post customer details
        return customerService.save(customer);
    }

    /**
     *
     * @param customerId
     * @return deletes customer details based on customer-id
     */
    @RequestMapping(value = "/customer/delete", produces = {"application/json"}, method = RequestMethod.DELETE)
    public String deleteCustomer(@RequestParam String customerId) {
        // delete customer details based on customer-id
        customerService.deleteCustomer(customerId);
        return "customer deleted!!";
    }
}
