package com.example;

import com.fasterxml.jackson.databind.JsonNode;

/*
 * Example of customer validator class 
 */
public class CustomerValidator {

    // Example of address validation, implemented on business logic side
    public boolean isValidAddress(JsonNode jsonPayload){
        String address = jsonPayload.get("address").asText();
        if(address.split(",").length!=4){
            return false;
        }else{
            return true;
        }
    }
    
}
