package com.amazon.aws.sample.exception;

public class OrderException extends RuntimeException {
    public OrderException(String str) {
        /** calling the constructor of parent Exception **/
        super(str);
    }
}