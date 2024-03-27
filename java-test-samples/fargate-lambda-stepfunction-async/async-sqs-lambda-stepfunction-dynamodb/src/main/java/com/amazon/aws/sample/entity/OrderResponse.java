package com.amazon.aws.sample.entity;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class OrderResponse {
    private String message;
    private String uuid;
}
