package com.amazon.aws.sample.entity;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import javax.validation.constraints.NotNull;

@Getter
@Setter
@NoArgsConstructor
public class OrderRequest {

    @NotNull(message = "The productName must not be null")
    private String productName;
    @NotNull(message = "The productId must not be null")
    private String productId;
    @NotNull(message = "The customerId must not be null")
    private String customerId;
    @NotNull(message = "The deliveryAddressCode must not be null")
    private String deliveryAddressCode;
    @NotNull(message = "The model must not be null")
    private String model;
    @NotNull(message = "The company must not be null")
    private String company;
    @NotNull(message = "The quantity must not be null")
    private String quantity;
    private String orderId;
}