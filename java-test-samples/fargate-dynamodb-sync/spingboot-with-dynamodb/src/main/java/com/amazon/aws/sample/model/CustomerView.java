package com.amazon.aws.sample.model;

import lombok.Data;

@Data
public class CustomerView {
    private String customerId;
    private String name;
    private String email;
}
